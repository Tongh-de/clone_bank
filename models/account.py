"""
账户模型
"""
from sqlalchemy import Column, Integer, String, Numeric, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from core.database import Base


class Account(Base):
    """账户表"""
    __tablename__ = "accounts"

    id = Column(Integer, primary_key=True, index=True)
    account_number = Column(String(20), unique=True, nullable=False, index=True)
    account_type = Column(String(20), default="savings")
    balance = Column(Numeric(15, 2), default=0.00)
    status = Column(String(20), default="active")
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    owner = relationship("User", back_populates="accounts")
    transactions = relationship("Transaction", foreign_keys="Transaction.account_id", back_populates="account", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Account {self.account_number}>"


class Transaction(Base):
    """交易记录表"""
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    transaction_type = Column(String(20), nullable=False)
    amount = Column(Numeric(15, 2), nullable=False)
    balance_before = Column(Numeric(15, 2), nullable=False)
    balance_after = Column(Numeric(15, 2), nullable=False)
    description = Column(String(255))
    account_id = Column(Integer, ForeignKey("accounts.id"), nullable=False)
    related_account_id = Column(Integer, ForeignKey("accounts.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.now, index=True)

    account = relationship("Account", foreign_keys=[account_id], back_populates="transactions")
    related_account = relationship("Account", foreign_keys=[related_account_id])

    def __repr__(self):
        return f"<Transaction {self.id} - {self.transaction_type}>"
