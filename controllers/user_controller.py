"""
用户控制器
"""
from fastapi import APIRouter, Depends, HTTPException, Request, Response
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from core.database import get_db
from models.user import User
from schemas import UserCreate, UserResponse, LoginRequest, ApiResponse
from core.auth import verify_password, get_password_hash, create_access_token
from core.logger import log_user_action, log_error, app_logger
from core import config

router = APIRouter(prefix="/api/auth", tags=["认证"])


@router.post("/register")
def register(user_data: UserCreate, request: Request, db: Session = Depends(get_db)):
    """用户注册"""
    client_ip = request.client.host if request.client else ""
    
    existing_user = db.query(User).filter(User.username == user_data.username).first()
    if existing_user:
        log_user_action(user_data.username, "注册失败-用户名已存在", "", client_ip)
        return ApiResponse.error("用户名已存在", code=400)
    
    if user_data.email:
        existing_email = db.query(User).filter(User.email == user_data.email).first()
        if existing_email:
            log_user_action(user_data.username, "注册失败-邮箱已被使用", "", client_ip)
            return ApiResponse.error("邮箱已被使用", code=400)
    
    try:
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
        
        log_user_action(new_user.username, "注册成功", f"邮箱: {new_user.email}", client_ip)
        app_logger.info(f"新用户注册: {new_user.username}")
        
        return ApiResponse.created(
            data={
                "id": new_user.id,
                "username": new_user.username,
                "full_name": new_user.full_name,
                "email": new_user.email,
                "role": new_user.role
            },
            message="注册成功"
        )
    except Exception as e:
        log_error("user_controller", e, "注册用户失败")
        return ApiResponse.error("注册失败", code=500)


@router.post("/login")
def login(login_data: LoginRequest, response: Response, request: Request, db: Session = Depends(get_db)):
    """用户登录"""
    client_ip = request.client.host if request.client else ""
    user_agent = request.headers.get("user-agent", "")[:50]
    
    user = db.query(User).filter(User.username == login_data.username).first()
    
    if not user or not verify_password(login_data.password, user.password_hash):
        log_user_action(login_data.username, "登录失败-密码错误", "", client_ip)
        return ApiResponse.error("用户名或密码错误", code=401)
    
    if not user.is_active:
        log_user_action(user.username, "登录失败-账户被禁用", "", client_ip)
        return ApiResponse.error("账户已被禁用", code=403)
    
    user.last_login = datetime.now()
    db.commit()
    
    access_token = create_access_token(
        data={"sub": user.username},
        expires_delta=timedelta(minutes=config.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        max_age=config.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        samesite="lax"
    )
    
    log_user_action(user.username, "登录成功", f"User-Agent: {user_agent}", client_ip)
    app_logger.info(f"用户登录: {user.username} from {client_ip}")
    
    return ApiResponse.success(
        data={"username": user.username, "role": user.role, "full_name": user.full_name},
        message="登录成功"
    )


@router.post("/logout")
def logout(response: Response, request: Request, db: Session = Depends(get_db)):
    """用户登出"""
    from core.auth import get_current_user
    import asyncio
    
    async def get_user():
        return await get_current_user(request, db)
    
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    
    user = loop.run_until_complete(get_user())
    username = user.username if user else "unknown"
    client_ip = request.client.host if request.client else ""
    
    response.delete_cookie("access_token")
    log_user_action(username, "退出登录", "", client_ip)
    
    return ApiResponse.success(message="已退出登录")


@router.get("/me")
def get_current_user_info(request: Request, db: Session = Depends(get_db)):
    """获取当前用户信息"""
    from core.auth import require_login
    import asyncio
    
    async def get_user():
        return await require_login(request, db)
    
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    
    user = loop.run_until_complete(get_user())
    
    return ApiResponse.success(
        data={
            "id": user.id,
            "username": user.username,
            "full_name": user.full_name,
            "email": user.email,
            "role": user.role,
            "is_active": user.is_active,
            "created_at": user.created_at.isoformat() if user.created_at else None,
            "last_login": user.last_login.isoformat() if user.last_login else None
        },
        message="获取成功"
    )
