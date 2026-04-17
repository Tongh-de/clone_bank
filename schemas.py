"""
Pydantic Schemas - 数据验证模型
"""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from decimal import Decimal


# ============ 用户相关 ============
class UserBase(BaseModel):
    username: str
    full_name: str
    email: Optional[str] = None


class UserCreate(UserBase):
    password: str


class UserResponse(UserBase):
    id: int
    role: str
    is_active: bool
    created_at: datetime
    last_login: Optional[datetime] = None

    class Config:
        from_attributes = True


# ============ 认证相关 ============
class LoginRequest(BaseModel):
    username: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None


# ============ 账户相关 ============
class AccountCreate(BaseModel):
    account_type: str = "savings"


class AccountResponse(BaseModel):
    id: int
    account_number: str
    account_type: str
    balance: Decimal
    status: str
    owner_id: int
    created_at: datetime

    class Config:
        from_attributes = True


class AccountListResponse(BaseModel):
    id: int
    account_number: str
    account_type: str
    balance: Decimal
    status: str
    owner_name: str
    created_at: datetime

    class Config:
        from_attributes = True


# ============ 交易相关 ============
class TransactionRequest(BaseModel):
    account_number: str
    amount: Decimal


class TransferRequest(BaseModel):
    from_account: str
    to_account: str
    amount: Decimal
    description: Optional[str] = None


class TransactionResponse(BaseModel):
    id: int
    transaction_type: str
    amount: Decimal
    balance_before: Decimal
    balance_after: Decimal
    description: Optional[str] = None
    account_id: int
    related_account_id: Optional[int] = None
    created_at: datetime

    class Config:
        from_attributes = True


# ============ 报表相关 ============
class ReportRequest(BaseModel):
    report_type: str  # daily, monthly, account
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    account_number: Optional[str] = None
    format: str = "pdf"  # pdf, excel


class ReportResponse(BaseModel):
    success: bool
    message: str
    file_path: Optional[str] = None
