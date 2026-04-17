"""
用户控制器
"""
from fastapi import APIRouter, Depends, HTTPException, Request, Response
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from database import get_db
from models.user import User
from schemas import UserCreate, UserResponse, LoginRequest, Token
from auth import verify_password, get_password_hash, create_access_token
import config

router = APIRouter(prefix="/api/auth", tags=["认证"])


@router.post("/register", response_model=UserResponse)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """用户注册"""
    # 检查用户名是否存在
    existing_user = db.query(User).filter(User.username == user_data.username).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="用户名已存在")
    
    # 检查邮箱是否存在
    if user_data.email:
        existing_email = db.query(User).filter(User.email == user_data.email).first()
        if existing_email:
            raise HTTPException(status_code=400, detail="邮箱已被使用")
    
    # 创建用户
    new_user = User(
        username=user_data.username,
        password_hash=get_password_hash(user_data.password),
        full_name=user_data.full_name,
        email=user_data.email,
        role="user"
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return new_user


@router.post("/login")
def login(login_data: LoginRequest, response: Response, db: Session = Depends(get_db)):
    """用户登录"""
    user = db.query(User).filter(User.username == login_data.username).first()
    
    if not user or not verify_password(login_data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="用户名或密码错误")
    
    if not user.is_active:
        raise HTTPException(status_code=403, detail="账户已被禁用")
    
    # 更新最后登录时间
    user.last_login = datetime.now()
    db.commit()
    
    # 创建令牌
    access_token = create_access_token(
        data={"sub": user.username},
        expires_delta=timedelta(minutes=config.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    
    # 设置Cookie
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        max_age=config.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        samesite="lax"
    )
    
    return {"message": "登录成功", "username": user.username, "role": user.role}


@router.post("/logout")
def logout(response: Response):
    """用户登出"""
    response.delete_cookie("access_token")
    return {"message": "已退出登录"}


@router.get("/me", response_model=UserResponse)
def get_current_user_info(request: Request, db: Session = Depends(get_db)):
    """获取当前用户信息"""
    from auth import get_current_user, require_login
    import asyncio
    
    async def get_user():
        return await require_login(request, db)
    
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    
    user = loop.run_until_complete(get_user())
    return user
