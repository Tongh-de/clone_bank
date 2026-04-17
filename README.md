# Bank Account Management System

#### 介绍
一个专注于银行账户管理的开源项目，采用 FastAPI + MySQL 构建，提供账户管理、交易记录分析、报表导出等功能。

#### 软件架构
- **前端**：HTML + Bootstrap 5
- **后端**：FastAPI (Python)
- **数据库**：MySQL
- **认证**：JWT Token
- **架构模式**：MVC

#### 功能模块
- 用户登录认证
- 账户管理（开户、销户、冻结）
- 存款/取款/转账
- 交易记录查询
- 报表导出（PDF/Excel）

#### 安装教程

1. 安装 Python 3.9+
2. 安装 MySQL 8.0+
3. 创建数据库：
```sql
CREATE DATABASE bank_db DEFAULT CHARSET utf8mb4;
```
4. 安装依赖：
```bash
pip install -r requirements.txt
```
5. 修改 `config.py` 中的数据库配置
6. 运行项目：
```bash
uvicorn main:app --reload
```
7. 访问 http://localhost:8000

#### 使用说明

- 初始管理员账号：admin / admin123
- 账户余额单位：元
- 所有金额保留2位小数
