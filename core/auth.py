"""
认证工具
"""
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from core.database import get_db
from core.logger import log_user_action, log_error
from core import config

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证密码"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """哈希密码"""
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """创建JWT令牌"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=config.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, config.SECRET_KEY, algorithm=config.ALGORITHM)
    return encoded_jwt


def decode_token(token: str) -> Optional[str]:
    """解码JWT令牌"""
    try:
        payload = jwt.decode(token, config.SECRET_KEY, algorithms=[config.ALGORITHM])
        username: str = payload.get("sub")
        return username
    except JWTError:
        return None


async def get_current_user(request: Request, db: Session = Depends(get_db)):
    """获取当前用户"""
    token = request.cookies.get("access_token")
    
    if not token:
        return None
        
    username = decode_token(token)
    if not username:
        return None
        
    from models.user import User
    user = db.query(User).filter(User.username == username).first()
    return user


async def require_login(request: Request, db: Session = Depends(get_db)):
    """要求登录"""
    user = await get_current_user(request, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_302_FOUND,
            headers={"Location": "/login"}
        )
    return user
