"""
转账控制器
"""
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from decimal import Decimal
from core.database import get_db
from models.account import Account, Transaction
from schemas import TransferRequest, ApiResponse
from core.auth import require_login
from core.logger import log_transaction, log_user_action

router = APIRouter(prefix="/api/transfer", tags=["转账"])


@router.post("/")
async def transfer(
    request: Request,
    transfer_data: TransferRequest,
    db: Session = Depends(get_db)
):
    """转账"""
    user = await require_login(request, db)
    
    if transfer_data.amount <= 0:
        return ApiResponse.error("转账金额必须大于0", code=400)
    
    from_account = db.query(Account).filter(
        Account.account_number == transfer_data.from_account,
        Account.owner_id == user.id
    ).first()
    
    if not from_account:
        return ApiResponse.error("转出账户不存在", code=404)
    
    if from_account.status != "active":
        return ApiResponse.error("转出账户状态异常", code=400)
    
    to_account = db.query(Account).filter(
        Account.account_number == transfer_data.to_account
    ).first()
    
    if not to_account:
        return ApiResponse.error("转入账户不存在", code=404)
    
    if to_account.status != "active":
        return ApiResponse.error("转入账户状态异常", code=400)
    
    if from_account.id == to_account.id:
        return ApiResponse.error("不能给自己转账", code=400)
    
    if from_account.balance < Decimal(str(transfer_data.amount)):
        return ApiResponse.error("余额不足", code=400)
    
    amount = Decimal(str(transfer_data.amount))
    from_balance_before = from_account.balance
    to_balance_before = to_account.balance
    
    from_account.balance -= amount
    to_account.balance += amount
    
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
    
    log_transaction(transfer_data.from_account, "转出", float(amount), float(from_account.balance), f"至 {transfer_data.to_account}")
    log_transaction(transfer_data.to_account, "转入", float(amount), float(to_account.balance), f"来自 {transfer_data.from_account}")
    log_user_action(user.username, "转账", 
                   f"从 {transfer_data.from_account} 至 {transfer_data.to_account}, 金额: ¥{float(amount)}",
                   request.client.host if request.client else "")
    
    return ApiResponse.success(
        data={
            "amount": float(amount),
            "from_account": transfer_data.from_account,
            "to_account": transfer_data.to_account,
            "remaining_balance": float(from_account.balance),
            "from_transaction_id": from_transaction.id,
            "to_transaction_id": to_transaction.id
        },
        message="转账成功"
    )
