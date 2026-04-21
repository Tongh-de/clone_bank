"""
银行账户管理系统 - 主入口
MVC架构 - FastAPI + MySQL
"""
from fastapi import FastAPI, Request, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from core.database import engine, Base, get_db
from models.user import User
from models.account import Account, Transaction
from core.auth import get_current_user, get_password_hash
from core.logger import app_logger
from core import config

# 创建表
Base.metadata.create_all(bind=engine)

app_logger.info("=" * 50)
app_logger.info("银行账户管理系统启动")
app_logger.info("=" * 50)

app = FastAPI(
    title="银行账户管理系统",
    description="MVC架构的银行账户管理开源项目",
    version="1.0.0"
)

# 静态文件和模板
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="frontend")

# 注册路由
from controllers.user_controller import router as auth_router
from controllers.account_controller import router as account_router
from controllers.transfer_controller import router as transfer_router
from controllers.report_controller import router as report_router
from controllers.ai_controller import router as ai_router
from controllers.email_controller import router as email_router
from services.map_service import router as map_router

app.include_router(auth_router)
app.include_router(account_router)
app.include_router(transfer_router)
app.include_router(report_router)
app.include_router(ai_router)
app.include_router(email_router)
app.include_router(map_router)


# ============ 页面路由 ============

@app.get("/", response_class=HTMLResponse)
async def home(request: Request, db: Session = Depends(get_db)):
    """首页"""
    user = await get_current_user(request, db)
    if not user:
        return RedirectResponse(url="/login", status_code=302)
    return templates.TemplateResponse("index.html", {"request": request, "user": user})


@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    """登录页"""
    return templates.TemplateResponse("login.html", {"request": request})


@app.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    """注册页"""
    return templates.TemplateResponse("register.html", {"request": request})


@app.get("/accounts", response_class=HTMLResponse)
async def accounts_page(request: Request, db: Session = Depends(get_db)):
    """账户列表页"""
    user = await get_current_user(request, db)
    if not user:
        return RedirectResponse(url="/login", status_code=302)
    return templates.TemplateResponse("accounts.html", {"request": request, "user": user})


@app.get("/account/{account_number}", response_class=HTMLResponse)
async def account_detail_page(request: Request, account_number: str, db: Session = Depends(get_db)):
    """账户详情页"""
    user = await get_current_user(request, db)
    if not user:
        return RedirectResponse(url="/login", status_code=302)
    return templates.TemplateResponse("account_detail.html", {"request": request, "user": user, "account_number": account_number})


@app.get("/transfer", response_class=HTMLResponse)
async def transfer_page(request: Request, db: Session = Depends(get_db)):
    """转账页"""
    user = await get_current_user(request, db)
    if not user:
        return RedirectResponse(url="/login", status_code=302)
    return templates.TemplateResponse("transfer.html", {"request": request, "user": user})


@app.get("/reports", response_class=HTMLResponse)
async def reports_page(request: Request, db: Session = Depends(get_db)):
    """报表页"""
    user = await get_current_user(request, db)
    if not user:
        return RedirectResponse(url="/login", status_code=302)
    return templates.TemplateResponse("reports.html", {"request": request, "user": user})


@app.get("/ai-chat", response_class=HTMLResponse)
async def ai_chat_page(request: Request, db: Session = Depends(get_db)):
    """AI客服页"""
    user = await get_current_user(request, db)
    if not user:
        return RedirectResponse(url="/login", status_code=302)
    return templates.TemplateResponse("ai_chat.html", {"request": request, "user": user})


@app.get("/email", response_class=HTMLResponse)
async def email_page(request: Request, db: Session = Depends(get_db)):
    """发送邮件页"""
    user = await get_current_user(request, db)
    if not user:
        return RedirectResponse(url="/login", status_code=302)
    return templates.TemplateResponse("email.html", {"request": request, "user": user})


@app.get("/map", response_class=HTMLResponse)
async def map_page(request: Request, db: Session = Depends(get_db)):
    """网点地图页"""
    user = await get_current_user(request, db)
    if not user:
        return RedirectResponse(url="/login", status_code=302)
    return templates.TemplateResponse("map.html", {
        "request": request, 
        "user": user,
        "amap_key": config.AMAP_WEB_KEY
    })


# ============ 初始化管理员 ============

def init_admin():
    """初始化管理员账户"""
    db = next(get_db())
    try:
        admin = db.query(User).filter(User.username == "admin").first()
        if not admin:
            admin = User(
                username="admin",
                password_hash=get_password_hash("admin123"),
                full_name="系统管理员",
                email="admin@bank.com",
                role="admin"
            )
            db.add(admin)
            db.commit()
            print("管理员账户已创建: admin / admin123")
        else:
            admin.password_hash = get_password_hash("admin123")
            db.commit()
            print("管理员密码已更新: admin / admin123")
    except Exception as e:
        print(f"初始化管理员失败: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    import uvicorn
    
    init_admin()
    
    app_logger.info(f"银行 {config.BANK_NAME} 账户管理系统")
    app_logger.info("=" * 50)
    app_logger.info(f"访问地址: http://localhost:8080")
    app_logger.info(f"API文档: http://localhost:8080/docs")
    app_logger.info(f"默认账号: admin / admin123")
    app_logger.info("=" * 50)
    
    uvicorn.run(app, host="127.0.0.1", port=8080)
