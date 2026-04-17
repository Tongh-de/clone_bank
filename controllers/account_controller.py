"""
账户控制器
"""
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime
from decimal import Decimal
import random
import string
from database import get_db
from models.user import User
from models.account import Account, Transaction
from schemas import AccountCreate, AccountResponse, AccountListResponse, TransactionResponse
from auth import require_login
from config import PAGE_SIZE

router = APIRouter(prefix="/api/accounts", tags=["账户管理"])


def generate_account_number() -> str:
    """生成账户号"""
    prefix = "6228"
    random_part = ''.join(random.choices(string.digits, k=12))
    return prefix + random_part


@router.post("/create", response_model=AccountResponse)
async def create_account(
    request: Request,
    account_data: AccountCreate,
    db: Session = Depends(get_db)
):
    """创建账户"""
    user = await require_login(request, db)
    
    # 生成唯一账户号
    while True:
        account_number = generate_account_number()
        existing = db.query(Account).filter(Account.account_number == account_number).first()
        if not existing:
            break
    
    # 创建账户
    new_account = Account(
        account_number=account_number,
        account_type=account_data.account_type,
        balance=Decimal("0.00"),
        status="active",
        owner_id=user.id
    )
    db.add(new_account)
    db.commit()
    db.refresh(new_account)
    
    return new_account


async def list_accounts(
    request: Request,
    page: int = 1,
    status_filter: str = None,
    db: Session = Depends(get_db)
):
    """获取账户列表"""
    user = await require_login(request, db)
    
    query = db.query(Account).filter(Account.owner_id == user.id)

    if status_filter:
        query = query.filter(Account.status == status_filter)
    
    query = query.order_by(Account.created_at.desc())
    offset = (page - 1) * PAGE_SIZE
    
    accounts = query.offset(offset).limit(PAGE_SIZE).all()

    return accounts


@router.get("/{account_number}", response_model=AccountResponse)
async def get_account(
    request: Request,
    account_number: str,
    db: Session = Depends(get_db)
):
    """获取账户详情"""
    user = await require_login(request, db)
    
    account = db.query(Account).filter(
        Account.account_number == account_number,
        Account.owner_id == user.id
    ).first()
    
    if not account:
        raise HTTPException(status_code=404, detail="账户不存在")
    
    return account


@router.post("/{account_number}/freeze")
async def freeze_account(
    request: Request,
    account_number: str,
    db: Session = Depends(get_db)
):
    """冻结账户"""
    user = await require_login(request, db)
    
    account = db.query(Account).filter(
        Account.account_number == account_number,
        Account.owner_id == user.id
    ).first()
    
    if not account:
        raise HTTPException(status_code=404, detail="账户不存在")
    
    if account.status == "frozen":
        raise HTTPException(status_code=400, detail="账户已被冻结")
    
    account.status = "frozen"
    db.commit()
    
    return {"message": "账户已冻结"}


@router.post("/{account_number}/unfreeze")
async def unfreeze_account(
    request: Request,
    account_number: str,
    db: Session = Depends(get_db)
):
    """解冻账户"""
    user = await require_login(request, db)
    
    account = db.query(Account).filter(
        Account.account_number == account_number,
        Account.owner_id == user.id
    ).first()
    
    if not account:
        raise HTTPException(status_code=404, detail="账户不存在")
    
    if account.status != "frozen":
        raise HTTPException(status_code=400, detail="账户未被冻结")
    
    account.status = "active"
    db.commit()
    
    return {"message": "账户已解冻"}


@router.post("/{account_number}/close")
async def close_account(
    request: Request,
    account_number: str,
    db: Session = Depends(get_db)
):
    """销户"""
    user = await require_login(request, db)
    
    account = db.query(Account).filter(
        Account.account_number == account_number,
        Account.owner_id == user.id
    ).first()
    
    if not account:
        raise HTTPException(status_code=404, detail="账户不存在")
    
    if account.balance > 0:
        raise HTTPException(status_code=400, detail="账户余额必须为0才能销户")
    
    account.status = "closed"
    db.commit()
    
    return {"message": "账户已销户"}


@router.post("/{account_number}/deposit")
async def deposit(
    request: Request,
    account_number: str,
    amount: float,
    db: Session = Depends(get_db)
):
    """存款"""
    user = await require_login(request, db)
    
    if amount <= 0:
        raise HTTPException(status_code=400, detail="存款金额必须大于0")
    
    account = db.query(Account).filter(
        Account.account_number == account_number,
        Account.owner_id == user.id
    ).first()
    
    if not account:
        raise HTTPException(status_code=404, detail="账户不存在")
    
    if account.status != "active":
        raise HTTPException(status_code=400, detail="账户状态异常")
    
    balance_before = account.balance
    account.balance += Decimal(str(amount))
    balance_after = account.balance
    
    # 记录交易
    transaction = Transaction(
        transaction_type="deposit",
        amount=Decimal(str(amount)),
        balance_before=balance_before,
        balance_after=balance_after,
        description="存款",
        account_id=account.id
    )
    db.add(transaction)
    db.commit()
    
    return {
        "message": "存款成功",
        "amount": amount,
        "balance": float(balance_after)
    }


@router.post("/{account_number}/withdraw")
async def withdraw(
    request: Request,
    account_number: str,
    amount: float,
    db: Session = Depends(get_db)
):
    """取款"""
    user = await require_login(request, db)
    
    if amount <= 0:
        raise HTTPException(status_code=400, detail="取款金额必须大于0")
    
    account = db.query(Account).filter(
        Account.account_number == account_number,
        Account.owner_id == user.id
    ).first()
    
    if not account:
        raise HTTPException(status_code=404, detail="账户不存在")
    
    if account.status != "active":
        raise HTTPException(status_code=400, detail="账户状态异常")
    
    if account.balance < Decimal(str(amount)):
        raise HTTPException(status_code=400, detail="余额不足")
    
    balance_before = account.balance
    account.balance -= Decimal(str(amount))
    balance_after = account.balance
    
    # 记录交易
    transaction = Transaction(
        transaction_type="withdraw",
        amount=Decimal(str(amount)),
        balance_before=balance_before,
        balance_after=balance_after,
        description="取款",
        account_id=account.id
    )
    db.add(transaction)
    db.commit()
    
    return {
        "message": "取款成功",
        "amount": amount,
        "balance": float(balance_after)
    }


@router.get("/{account_number}/transactions", response_model=list[TransactionResponse])
async def get_transactions(
    request: Request,
    account_number: str,
    page: int = 1,
    db: Session = Depends(get_db)
):
    """获取交易记录"""
    user = await require_login(request, db)
    
    account = db.query(Account).filter(
        Account.account_number == account_number,
        Account.owner_id == user.id
    ).first()
    
    if not account:
        raise HTTPException(status_code=404, detail="账户不存在")
    
    query = db.query(Transaction).filter(Transaction.account_id == account.id)
    query = query.order_by(Transaction.created_at.desc())
    
    offset = (page - 1) * PAGE_SIZE
    transactions = query.offset(offset).limit(PAGE_SIZE).all()
    
    return transactions
