# 银行账户管理系统

基于 FastAPI + MySQL 构建的银行账户管理系统，采用 MVC 架构，集成了 AI 智能客服、邮件发送和地图服务等企业级功能。

## 项目结构

```
bank_count_yang/
├── core/                          # 核心配置层
│   ├── config.py                  # 系统配置
│   ├── database.py                # 数据库连接
│   ├── logger.py                  # 日志系统
│   └── auth.py                    # JWT认证
├── models/                        # 数据模型层
│   ├── user.py                    # 用户模型
│   └── account.py                 # 账户/交易模型
├── controllers/                   # 控制器层
│   ├── user_controller.py         # 用户认证
│   ├── account_controller.py      # 账户管理
│   ├── transfer_controller.py     # 转账
│   ├── report_controller.py       # 报表
│   ├── ai_controller.py           # AI客服
│   └── email_controller.py        # 邮件发送
├── services/                      # 服务层
│   ├── ai_service.py              # Ollama AI服务
│   ├── ai_customer_service.py      # 通义千问客服
│   ├── email_service.py            # 邮件服务
│   └── map_service.py              # 地图服务
├── frontend/                      # 前端页面
│   ├── base.html                  # 基础模板
│   ├── login.html                 # 登录页
│   ├── register.html              # 注册页
│   ├── index.html                 # 首页
│   ├── accounts.html               # 账户管理
│   ├── account_detail.html        # 账户详情
│   ├── transfer.html              # 转账页面
│   ├── reports.html               # 报表页面
│   ├── ai_chat.html               # AI客服
│   ├── email.html                 # 邮件发送
│   └── map.html                   # 网点地图
├── static/css/                    # 样式文件
├── schemas.py                     # 数据验证模型
├── main.py                        # 应用入口
└── requirements.txt              # 依赖
```

## 功能特性

### 账户管理
- 用户注册 / 登录（JWT Token认证）
- 多账户类型支持（储蓄账户、信用卡等）
- 存款 / 取款 / 转账
- 账户冻结 / 解冻 / 注销
- 交易记录查询
- 账户统计（今日数据）

### 报表系统
- PDF 报表导出（基于 ReportLab）
- Excel 报表导出（基于 openpyxl）
- 按时间范围筛选
- 按账户筛选
- 报表下载

### AI 智能助手
- Ollama 本地 AI 对话（支持流式输出）
- 通义千问云端对话
- 天气查询（OpenWeatherMap）
- 银行网点位置搜索（高德地图）
- 多种 AI 模型切换

### AI 邮件生成
- 10+ 种银行常用邮件模板
- 支持自定义邮件用途，灵活输入
- AI 一键生成专业邮件内容
- 支持客户姓名和附加说明
- 生成后可手动编辑修改

### 邮件发送
- SMTP 163 邮箱发送
- 支持自定义主题和内容

### 网点地图
- 高德地图集成
- 银行网点搜索
- 位置展示

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

- 网址：http://localhost:8080
- API文档：http://localhost:8080/docs
- 默认账号：`admin` / `admin123`

## API 接口

### 认证接口 `/api/auth`

| 接口 | 方法 | 说明 |
|------|------|------|
| `/api/auth/register` | POST | 用户注册 |
| `/api/auth/login` | POST | 用户登录 |
| `/api/auth/logout` | POST | 用户登出 |
| `/api/auth/me` | GET | 获取当前用户信息 |

### 账户接口 `/api/accounts`

| 接口 | 方法 | 说明 |
|------|------|------|
| `/api/accounts/create` | POST | 创建账户 |
| `/api/accounts/list` | GET | 获取账户列表 |
| `/api/accounts/stats/today` | GET | 今日统计 |
| `/api/accounts/{account_number}` | GET | 账户详情 |
| `/api/accounts/{account_number}/freeze` | POST | 冻结账户 |
| `/api/accounts/{account_number}/unfreeze` | POST | 解冻账户 |
| `/api/accounts/{account_number}/close` | POST | 注销账户 |
| `/api/accounts/{account_number}/deposit` | POST | 存款 |
| `/api/accounts/{account_number}/withdraw` | POST | 取款 |
| `/api/accounts/{account_number}/transactions` | GET | 交易记录 |

### 转账接口 `/api/transfer`

| 接口 | 方法 | 说明 |
|------|------|------|
| `/api/transfer/` | POST | 转账 |

### 报表接口 `/api/reports`

| 接口 | 方法 | 说明 |
|------|------|------|
| `/api/reports/generate` | POST | 生成报表 |
| `/api/reports/download/{filename}` | GET | 下载报表 |
| `/api/reports/list` | GET | 报表列表 |

### AI接口 `/api/ai`

| 接口 | 方法 | 说明 |
|------|------|------|
| `/api/ai/chat` | POST | AI对话 |
| `/api/ai/chat/stream` | POST | 流式AI对话 |
| `/api/ai/chat/advanced` | POST | 高级AI对话 |
| `/api/ai/models` | GET | 获取可用模型 |

### 邮件接口 `/api/email`

| 接口 | 方法 | 说明 |
|------|------|------|
| `/api/email/send` | POST | 发送邮件 |
| `/api/email/generate` | POST | AI生成邮件 |

### 地图接口 `/api/map`

| 接口 | 方法 | 说明 |
|------|------|------|
| `/api/map/search` | GET | 搜索银行网点 |

## 配置说明

### AI 配置

#### Ollama 本地模型

确保已安装 Ollama 并下载模型：

```bash
# 安装 Ollama
# 下载模型
ollama pull qwen:0.5b

# 启动服务
ollama serve
```

#### 通义千问（云端）

编辑 `core/config.py` 配置 API Key：

```python
DASHSCOPE_API_KEY = "your-api-key"
```

### 邮件配置

编辑 `core/config.py` 配置 SMTP：

```python
EMAIL_HOST = "smtp.163.com"
EMAIL_USER = "your-email@163.com"
EMAIL_PASS = "your-authorization-code"
EMAIL_PORT = 25
```

### 高德地图配置

```python
AMAP_WEB_KEY = "your-web-api-key"      # 前端使用
AMAP_SERVER_KEY = "your-server-api-key"  # 后端使用
```

## 技术栈

- **后端**：FastAPI, SQLAlchemy, PyMySQL
- **前端**：Bootstrap 5, HTML/CSS/JavaScript, Jinja2
- **AI**：Ollama, 通义千问 API
- **地图**：高德地图 Web API
- **邮件**：SMTPLib
- **数据库**：MySQL
- **报表**：ReportLab, openpyxl
