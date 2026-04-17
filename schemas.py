"""
数据模型
"""
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class UserCreate(BaseModel):
    username: str
    password: str
    full_name: str
    email: Optional[str] = None


class UserResponse(BaseModel):
    id: int
    username: str
    full_name: str
    email: Optional[str]
    role: str
    is_active: bool
    created_at: datetime
    last_login: Optional[datetime]

    class Config:
        from_attributes = True


class LoginRequest(BaseModel):
    username: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str


class AccountCreate(BaseModel):
    account_type: str = "savings"
    initial_balance: float = 0.0


class AccountResponse(BaseModel):
    id: int
    account_number: str
    account_type: str
    balance: float
    status: str
    owner_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class AccountListResponse(BaseModel):
    accounts: List[AccountResponse]
    total: int


class TransactionResponse(BaseModel):
    id: int
    transaction_type: str
    amount: float
    balance_before: float
    balance_after: float
    description: Optional[str]
    account_id: int
    related_account_id: Optional[int]
    created_at: datetime

    class Config:
        from_attributes = True


class TransferRequest(BaseModel):
    from_account: str
    to_account: str
    amount: float
    description: Optional[str] = None


class ChatMessage(BaseModel):
    role: str
    content: str


class ReportRequest(BaseModel):
    report_type: str  # daily, monthly, account
    format: Optional[str] = "pdf"  # pdf 或 excel
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    account_number: Optional[str] = None


class ReportResponse(BaseModel):
    success: bool
    message: str
    file_path: Optional[str] = None
    report_type: Optional[str] = None
