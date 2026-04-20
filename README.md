# 银行账户管理系统

基于 FastAPI + MySQL 构建的银行账户管理系统，采用 MVC 架构，支持 AI 智能客服和邮件发送功能。

## 项目结构

```
bank_count_yang/
├── core/                      # 核心配置层
│   ├── config.py              # 配置管理
│   ├── database.py            # 数据库连接
│   ├── logger.py             # 日志系统
│   └── auth.py               # 认证工具
├── models/                    # 数据模型层
│   ├── user.py               # 用户模型
│   └── account.py            # 账户/交易模型
├── controllers/               # 控制器层
│   ├── user_controller.py    # 用户认证
│   ├── account_controller.py # 账户管理
│   ├── transfer_controller.py # 转账
│   ├── report_controller.py  # 报表
│   ├── ai_controller.py      # AI客服
│   └── email_controller.py   # 邮件发送
├── services/                  # 服务层
│   ├── ai_service.py         # Ollama AI服务
│   ├── ai_customer_service.py # 通义千问客服
│   └── email_service.py      # 邮件服务
├── frontend/                   # 前端页面
│   ├── base.html             # 基础模板
│   ├── login.html            # 登录页
│   ├── register.html         # 注册页
│   ├── accounts.html         # 账户管理
│   ├── transfer.html         # 转账页面
│   ├── reports.html          # 报表页面
│   ├── ai_chat.html          # AI客服
│   └── email.html            # 邮件发送
├── static/css/               # 样式文件
├── schemas.py                # 数据验证
├── main.py                   # 应用入口
└── requirements.txt          # 依赖
```

## 功能特性

### 账户管理
- 用户注册 / 登录（JWT认证）
- 账户创建、存款、取款
- 转账功能
- 交易记录查询

### 报表系统
- PDF 报表导出
- Excel 报表导出
- 按时间/账户筛选

### AI 智能助手
- Ollama 本地 AI 对话
- 天气查询（OpenWeatherMap）
- 银行网点位置搜索
- 通义千问云端对话

### AI 邮件生成
- 10+ 种银行常用邮件模板
- AI 一键生成专业邮件内容
- 支持自定义客户姓名和附加说明
- 生成后可手动编辑修改

### 邮件发送
- SMTP 163 邮箱发送
- 支持自定义主题和内容

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置数据库

编辑 `core/config.py` 中的数据库连接配置：

```python
DATABASE_URL = "mysql+pymysql://root:密码@localhost:3306/bank_db"
```

### 3. 初始化数据库

```bash
mysql -u root -p
CREATE DATABASE bank_db CHARACTER SET utf8mb4;
```

### 4. 启动服务

```bash
python main.py
```

### 5. 访问系统

- 网址：http://localhost:8000
- 默认账号：`admin` / `admin123`

## API 接口

| 接口 | 方法 | 说明 |
|------|------|------|
| `/api/auth/login` | POST | 用户登录 |
| `/api/auth/register` | POST | 用户注册 |
| `/api/accounts` | GET | 获取账户列表 |
| `/api/accounts/create` | POST | 创建账户 |
| `/api/accounts/{id}/deposit` | POST | 存款 |
| `/api/accounts/{id}/withdraw` | POST | 取款 |
| `/api/transfer` | POST | 转账 |
| `/api/transactions` | GET | 交易记录 |
| `/api/reports/generate` | POST | 生成报表 |
| `/api/ai/chat` | POST | AI对话 |
| `/api/email/send` | POST | 发送邮件 |
| `/api/email/generate` | POST | AI生成邮件 |

## AI 配置

### Ollama 本地模型

确保已安装 Ollama 并下载模型：

```bash
# 安装 Ollama
# 下载模型
ollama pull qwen:0.5b

# 启动服务
ollama serve
```

### 通义千问（云端）

编辑 `core/config.py` 配置 API Key：

```python
DASHSCOPE_API_KEY = "your-api-key"
```

## 邮件配置

编辑 `core/config.py` 配置 SMTP：

```python
EMAIL_HOST = "smtp.163.com"
EMAIL_USER = "your-email@163.com"
EMAIL_PASS = "your授权码"
EMAIL_PORT = 25
```

## 技术栈

- **后端**：FastAPI, SQLAlchemy, PyMySQL
- **前端**：Bootstrap 5, HTML/CSS/JavaScript
- **AI**：Ollama, 通义千问 API
- **邮件**：SMTPLib
- **数据库**：MySQL
