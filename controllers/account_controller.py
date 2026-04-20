"""
账户控制器
"""
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from decimal import Decimal
import random
import string
from core.database import get_db
from models.user import User
from models.account import Account, Transaction
from schemas import AccountCreate, AccountResponse, TransactionResponse, ApiResponse
from core.auth import require_login
from core.logger import log_transaction, log_error, log_user_action
from core import config

router = APIRouter(prefix="/api/accounts", tags=["账户管理"])


def generate_account_number() -> str:
    """生成账户号"""
    prefix = "6228"
    random_part = ''.join(random.choices(string.digits, k=12))
    return prefix + random_part


@router.post("/create")
async def create_account(
    request: Request,
    account_data: AccountCreate,
    db: Session = Depends(get_db)
):
    """创建账户"""
    user = await require_login(request, db)
    
    while True:
        account_number = generate_account_number()
        existing = db.query(Account).filter(Account.account_number == account_number).first()
        if not existing:
            break
    
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
    
    return ApiResponse.created(
        data={
            "id": new_account.id,
            "account_number": new_account.account_number,
            "account_type": new_account.account_type,
            "balance": float(new_account.balance),
            "status": new_account.status,
            "created_at": new_account.created_at.isoformat()
        },
        message="账户创建成功"
    )


@router.get("/list")
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
    
    total = query.count()
    query = query.order_by(Account.created_at.desc())
    offset = (page - 1) * config.PAGE_SIZE
    
    accounts = query.offset(offset).limit(config.PAGE_SIZE).all()
    
    account_list = [{
        "id": acc.id,
        "account_number": acc.account_number,
        "account_type": acc.account_type,
        "balance": float(acc.balance),
        "status": acc.status,
        "created_at": acc.created_at.isoformat() if acc.created_at else None
    } for acc in accounts]
    
    return ApiResponse.page(account_list, total, page, config.PAGE_SIZE)


@router.get("/stats/today")
async def get_today_stats(
    request: Request,
    db: Session = Depends(get_db)
):
    """获取今日统计"""
    user = await require_login(request, db)
    
    today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    today_end = today_start + timedelta(days=1)
    
    user_accounts = db.query(Account).filter(Account.owner_id == user.id).all()
    account_ids = [acc.id for acc in user_accounts]
    
    if not account_ids:
        return ApiResponse.success(
            data={
                "today_deposit": 0,
                "today_withdraw": 0
            },
            message="获取成功"
        )
    
    today_transactions = db.query(Transaction).filter(
        Transaction.account_id.in_(account_ids),
        Transaction.created_at >= today_start,
        Transaction.created_at < today_end
    ).all()
    
    today_deposit = sum(float(t.amount) for t in today_transactions if t.transaction_type == "deposit")
    today_withdraw = sum(float(t.amount) for t in today_transactions if t.transaction_type == "withdraw")
    
    return ApiResponse.success(
        data={
            "today_deposit": today_deposit,
            "today_withdraw": today_withdraw
        },
        message="获取成功"
    )


@router.get("/{account_number}")
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
        return ApiResponse.error("账户不存在", code=404)
    
    return ApiResponse.success(
        data={
            "id": account.id,
            "account_number": account.account_number,
            "account_type": account.account_type,
            "balance": float(account.balance),
            "status": account.status,
            "created_at": account.created_at.isoformat() if account.created_at else None,
            "updated_at": account.updated_at.isoformat() if account.updated_at else None
        },
        message="获取成功"
    )


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
        return ApiResponse.error("账户不存在", code=404)
    
    if account.status == "frozen":
        return ApiResponse.error("账户已被冻结", code=400)
    
    account.status = "frozen"
    db.commit()
    
    return ApiResponse.success(message="账户已冻结")


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
        return ApiResponse.error("账户不存在", code=404)
    
    if account.status != "frozen":
        return ApiResponse.error("账户未被冻结", code=400)
    
    account.status = "active"
    db.commit()
    
    return ApiResponse.success(message="账户已解冻")


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
        return ApiResponse.error("账户不存在", code=404)
    
    if account.balance > 0:
        return ApiResponse.error("账户余额必须为0才能销户", code=400)
    
    account.status = "closed"
    db.commit()
    
    return ApiResponse.success(message="账户已销户")


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
        return ApiResponse.error("存款金额必须大于0", code=400)
    
    account = db.query(Account).filter(
        Account.account_number == account_number,
        Account.owner_id == user.id
    ).first()
    
    if not account:
        return ApiResponse.error("账户不存在", code=404)
    
    if account.status != "active":
        return ApiResponse.error("账户状态异常", code=400)
    
    balance_before = account.balance
    account.balance += Decimal(str(amount))
    balance_after = account.balance
    
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
    
    log_transaction(account_number, "存款", amount, float(balance_after), "成功")
    log_user_action(user.username, "存款", f"账户: {account_number}, 金额: ¥{amount}", request.client.host if request.client else "")
    
    return ApiResponse.success(
        data={
            "amount": amount,
            "balance": float(balance_after),
            "balance_before": float(balance_before),
            "transaction_id": transaction.id
        },
        message="存款成功"
    )


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
        return ApiResponse.error("取款金额必须大于0", code=400)
    
    account = db.query(Account).filter(
        Account.account_number == account_number,
        Account.owner_id == user.id
    ).first()
    
    if not account:
        return ApiResponse.error("账户不存在", code=404)
    
    if account.status != "active":
        return ApiResponse.error("账户状态异常", code=400)
    
    if account.balance < Decimal(str(amount)):
        return ApiResponse.error("余额不足", code=400)
    
    balance_before = account.balance
    account.balance -= Decimal(str(amount))
    balance_after = account.balance
    
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
    
    log_transaction(account_number, "取款", amount, float(balance_after), "成功")
    log_user_action(user.username, "取款", f"账户: {account_number}, 金额: ¥{amount}", request.client.host if request.client else "")
    
    return ApiResponse.success(
        data={
            "amount": amount,
            "balance": float(balance_after),
            "balance_before": float(balance_before),
            "transaction_id": transaction.id
        },
        message="取款成功"
    )


@router.get("/{account_number}/transactions")
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
        return ApiResponse.error("账户不存在", code=404)
    
    query = db.query(Transaction).filter(Transaction.account_id == account.id)
    total = query.count()
    query = query.order_by(Transaction.created_at.desc())
    
    offset = (page - 1) * config.PAGE_SIZE
    transactions = query.offset(offset).limit(config.PAGE_SIZE).all()
    
    transaction_list = [{
        "id": t.id,
        "transaction_type": t.transaction_type,
        "amount": float(t.amount),
        "balance_before": float(t.balance_before),
        "balance_after": float(t.balance_after),
        "description": t.description,
        "created_at": t.created_at.isoformat() if t.created_at else None
    } for t in transactions]
    
    return ApiResponse.page(transaction_list, total, page, config.PAGE_SIZE)
