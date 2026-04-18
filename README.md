# 银行账户管理系统

基于 FastAPI + MySQL 构建的银行账户管理系统，采用标准 MVC 架构。

## 项目结构

```
bank_count_yang/
├── core/                    # 核心配置层
│   ├── __init__.py
│   ├── config.py           # 配置管理
│   ├── database.py         # 数据库连接
│   ├── logger.py           # 日志系统
│   └── auth.py             # 认证工具
├── models/                  # 数据模型层
│   ├── __init__.py
│   ├── user.py             # 用户模型
│   └── account.py          # 账户/交易模型
├── views/                   # 视图层（HTML模板）
│   ├── templates/
│   └── static/
├── controllers/             # 控制器层
│   ├── __init__.py
│   ├── user_controller.py  # 用户认证
│   ├── account_controller.py # 账户管理
│   ├── transfer_controller.py # 转账
│   ├── report_controller.py # 报表
│   └── ai_controller.py     # AI客服
├── services/                # 服务层
│   ├── __init__.py
│   ├── ai_service.py       # 通义千问对话
│   └── ai_customer_service.py # AI客服
├── schemas.py               # 数据验证
├── main.py                  # 应用入口
└── requirements.txt        # 依赖
```

## MVC 架构说明

- **Model（模型层）**: `models/` - 定义数据结构和业务逻辑
- **View（视图层）**: `templates/` + `static/` - 前端页面和静态资源
- **Controller（控制器层）**: `controllers/` - 处理请求和响应
- **Services（服务层）**: `services/` - 业务逻辑服务
- **Core（核心层）**: `core/` - 配置、数据库、日志、认证

## 功能特性

- 用户注册/登录（JWT认证）
- 账户创建/存款/取款
- 转账功能
- 交易记录查询
- 报表生成（PDF/Excel）
- AI客服（天气查询、位置搜索）
- 文本生成图片

## 快速开始

```bash
# 安装依赖
pip install -r requirements.txt

# 启动服务
python main.py
```

访问 http://localhost:8000

默认账号: `admin` / `admin123`
