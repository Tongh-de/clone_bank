"""
转账控制器
"""
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from decimal import Decimal
from database import get_db
from models.account import Account, Transaction
from schemas import TransferRequest
from auth import require_login

router = APIRouter(prefix="/api/transfer", tags=["转账"])


@router.post("/")
async def transfer(
    request: Request,
    transfer_data: TransferRequest,
    db: Session = Depends(get_db)
):
    """转账"""
    user = await require_login(request, db)
    
    # 检查金额
    if transfer_data.amount <= 0:
        raise HTTPException(status_code=400, detail="转账金额必须大于0")
    
    # 获取转出账户
    from_account = db.query(Account).filter(
        Account.account_number == transfer_data.from_account,
        Account.owner_id == user.id
    ).first()
    
    if not from_account:
        raise HTTPException(status_code=404, detail="转出账户不存在")
    
    if from_account.status != "active":
        raise HTTPException(status_code=400, detail="转出账户状态异常")
    
    # 获取转入账户
    to_account = db.query(Account).filter(
        Account.account_number == transfer_data.to_account
    ).first()
    
    if not to_account:
        raise HTTPException(status_code=404, detail="转入账户不存在")
    
    if to_account.status != "active":
        raise HTTPException(status_code=400, detail="转入账户状态异常")
    
    if from_account.id == to_account.id:
        raise HTTPException(status_code=400, detail="不能给自己转账")
    
    # 检查余额
    if from_account.balance < Decimal(str(transfer_data.amount)):
        raise HTTPException(status_code=400, detail="余额不足")
    
    # 执行转账
    amount = Decimal(str(transfer_data.amount))
    from_balance_before = from_account.balance
    to_balance_before = to_account.balance
    
    from_account.balance -= amount
    to_account.balance += amount
    
    # 记录转出交易
    from_transaction = Transaction(
        transaction_type="transfer_out",
        amount=amount,
        balance_before=from_balance_before,
        balance_after=from_account.balance,
        description=f"转账至 {transfer_data.to_account}" + (f" - {transfer_data.description}" if transfer_data.description else ""),
        account_id=from_account.id,
        related_account_id=to_account.id
    )
    db.add(from_transaction)
    
    # 记录转入交易
    to_transaction = Transaction(
        transaction_type="transfer_in",
        amount=amount,
        balance_before=to_balance_before,
        balance_after=to_account.balance,
        description=f"转账来自 {transfer_data.from_account}" + (f" - {transfer_data.description}" if transfer_data.description else ""),
        account_id=to_account.id,
        related_account_id=from_account.id
    )
    db.add(to_transaction)
    
    db.commit()
    
    return {
        "message": "转账成功",
        "amount": float(amount),
        "from_account": transfer_data.from_account,
        "to_account": transfer_data.to_account,
        "remaining_balance": float(from_account.balance)
    }
