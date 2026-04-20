# 银行账户管理系统 - 数据库 ER 图

## 一、ER 图

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              users (用户表)                                  │
├─────────────────┬──────────────────┬─────────────────────────────────────────┤
│ 字段名           │ 类型              │ 说明                                     │
├─────────────────┼──────────────────┼─────────────────────────────────────────┤
│ id              │ INT (PK)         │ 主键，自增                              │
│ username        │ VARCHAR(50)      │ 用户名，唯一索引                         │
│ password_hash   │ VARCHAR(255)     │ 密码哈希                                 │
│ full_name       │ VARCHAR(100)     │ 姓名                                     │
│ email           │ VARCHAR(100)     │ 邮箱，唯一                               │
│ role            │ VARCHAR(20)      │ 角色 (admin/user)                       │
│ is_active       │ BOOLEAN          │ 是否激活                                 │
│ created_at      │ DATETIME         │ 创建时间                                 │
│ last_login      │ DATETIME         │ 最后登录时间                             │
└─────────────────┴──────────────────┴─────────────────────────────────────────┘
                                        │
                                        │ 1:N
                                        ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                            accounts (账户表)                                 │
├─────────────────┬──────────────────┬─────────────────────────────────────────┤
│ 字段名           │ 类型              │ 说明                                     │
├─────────────────┼──────────────────┼─────────────────────────────────────────┤
│ id              │ INT (PK)         │ 主键，自增                              │
│ account_number  │ VARCHAR(20)      │ 账号，唯一索引                           │
│ account_type    │ VARCHAR(20)      │ 账户类型 (savings/checking)             │
│ balance         │ DECIMAL(15,2)    │ 余额                                     │
│ status          │ VARCHAR(20)      │ 状态 (active/frozen/closed)            │
│ owner_id        │ INT (FK)         │ 所有者ID → users.id                     │
│ created_at      │ DATETIME         │ 创建时间                                 │
│ updated_at      │ DATETIME         │ 更新时间                                 │
└─────────────────┴──────────────────┴─────────────────────────────────────────┘
                                        │
                                        │ 1:N
                                        ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                          transactions (交易记录表)                            │
├─────────────────┬──────────────────┬─────────────────────────────────────────┤
│ 字段名           │ 类型              │ 说明                                     │
├─────────────────┼──────────────────┼─────────────────────────────────────────┤
│ id              │ INT (PK)         │ 主键，自增                              │
│ transaction_type│ VARCHAR(20)      │ 类型 (deposit/withdraw/transfer)       │
│ amount          │ DECIMAL(15,2)    │ 金额                                     │
│ balance_before  │ DECIMAL(15,2)    │ 交易前余额                               │
│ balance_after   │ DECIMAL(15,2)    │ 交易后余额                               │
│ description     │ VARCHAR(255)     │ 描述                                     │
│ account_id      │ INT (FK)         │ 主账户ID → accounts.id                  │
│ related_account_id│ INT (FK)       │ 关联账户ID → accounts.id (转账用)       │
│ created_at      │ DATETIME         │ 交易时间，索引                           │
└─────────────────┴──────────────────┴─────────────────────────────────────────┘
```

---

## 二、表关系说明

```
┌──────────┐       ┌──────────────┐       ┌──────────────┐
│  users  │───1:N──│   accounts   │───1:N──│ transactions │
└──────────┘       └──────────────┘       └──────────────┘
    │                                            ▲
    │                                            │
    └─────────────── owner_id ────────────────────┘

说明：
- users → accounts : 一个用户可以有多个账户 (1:N)
- accounts → transactions : 一个账户可以有多条交易记录 (1:N)
- transactions 自身 : 转账交易通过 related_account_id 实现自关联
```

---

## 三、详细字段说明

### users (用户表)

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| id | INT | PK, AUTO_INCREMENT | 主键 |
| username | VARCHAR(50) | UNIQUE, NOT NULL | 用户名，用于登录 |
| password_hash | VARCHAR(255) | NOT NULL | 密码哈希值（bcrypt加密） |
| full_name | VARCHAR(100) | NOT NULL | 用户真实姓名 |
| email | VARCHAR(100) | UNIQUE | 邮箱地址 |
| role | VARCHAR(20) | DEFAULT 'user' | 角色：admin-管理员 / user-普通用户 |
| is_active | BOOLEAN | DEFAULT TRUE | 账户是否激活 |
| created_at | DATETIME | DEFAULT NOW() | 注册时间 |
| last_login | DATETIME | NULL | 最后登录时间 |

### accounts (账户表)

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| id | INT | PK, AUTO_INCREMENT | 主键 |
| account_number | VARCHAR(20) | UNIQUE, NOT NULL | 银行卡号（16位随机数） |
| account_type | VARCHAR(20) | DEFAULT 'savings' | 账户类型：savings-储蓄 / checking-支票 |
| balance | DECIMAL(15,2) | DEFAULT 0.00 | 当前余额 |
| status | VARCHAR(20) | DEFAULT 'active' | 状态：active-正常 / frozen-冻结 / closed-销户 |
| owner_id | INT | FK → users.id, NOT NULL | 账户所有者 |
| created_at | DATETIME | DEFAULT NOW() | 开户时间 |
| updated_at | DATETIME | ON UPDATE NOW() | 最后更新时间 |

### transactions (交易记录表)

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| id | INT | PK, AUTO_INCREMENT | 主键 |
| transaction_type | VARCHAR(20) | NOT NULL | 交易类型：deposit-存款 / withdraw-取款 / transfer-转账 |
| amount | DECIMAL(15,2) | NOT NULL | 交易金额 |
| balance_before | DECIMAL(15,2) | NOT NULL | 交易前余额 |
| balance_after | DECIMAL(15,2) | NOT NULL | 交易后余额 |
| description | VARCHAR(255) | NULL | 交易描述/备注 |
| account_id | INT | FK → accounts.id, NOT NULL | 主账户（交易发起方） |
| related_account_id | INT | FK → accounts.id, NULL | 关联账户（转账目标，仅转账时使用） |
| created_at | DATETIME | INDEX, DEFAULT NOW() | 交易时间 |

---

## 四、业务场景说明

### 1. 用户注册登录
```
用户注册 → 创建 users 记录 → 设置 username/password
用户登录 → 验证 credentials → 更新 last_login
```

### 2. 创建账户
```
用户登录 → 创建账户 → 生成 account_number → 初始 balance=0
一个用户可拥有多个账户 (1:N)
```

### 3. 存款/取款
```
选择账户 → 输入金额 → 创建 transaction 记录
      ↓
更新 account.balance = balance_before ± amount
      ↓
记录 balance_before 和 balance_after
```

### 4. 转账
```
选择转出账户 → 输入目标账户 → 输入金额
      ↓
创建2条 transaction 记录：
  - 转出账户：transaction_type=transfer, amount=负数(或单独标记)
  - 转入账户：transaction_type=transfer, related_account_id=转出账户ID
      ↓
同时更新两个账户的 balance
```

---

## 五、索引设计

| 表名 | 索引类型 | 字段 | 说明 |
|------|----------|------|------|
| users | PRIMARY | id | 主键 |
| users | UNIQUE | username | 登录索引 |
| users | UNIQUE | email | 邮箱索引 |
| accounts | PRIMARY | id | 主键 |
| accounts | UNIQUE | account_number | 银行卡号索引 |
| accounts | INDEX | owner_id | 查询用户所有账户 |
| transactions | PRIMARY | id | 主键 |
| transactions | INDEX | account_id | 查询账户交易历史 |
| transactions | INDEX | created_at | 按时间排序查询 |
| transactions | INDEX | related_account_id | 查询关联交易 |

---

## 六、SQL 建表语句

```sql
-- 用户表
CREATE TABLE users (
    id INT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE,
    role VARCHAR(20) DEFAULT 'user',
    is_active BOOLEAN DEFAULT TRUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    last_login DATETIME,
    INDEX idx_username (username),
    INDEX idx_email (email)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 账户表
CREATE TABLE accounts (
    id INT PRIMARY KEY AUTO_INCREMENT,
    account_number VARCHAR(20) UNIQUE NOT NULL,
    account_type VARCHAR(20) DEFAULT 'savings',
    balance DECIMAL(15,2) DEFAULT 0.00,
    status VARCHAR(20) DEFAULT 'active',
    owner_id INT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (owner_id) REFERENCES users(id),
    INDEX idx_account_number (account_number),
    INDEX idx_owner_id (owner_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 交易记录表
CREATE TABLE transactions (
    id INT PRIMARY KEY AUTO_INCREMENT,
    transaction_type VARCHAR(20) NOT NULL,
    amount DECIMAL(15,2) NOT NULL,
    balance_before DECIMAL(15,2) NOT NULL,
    balance_after DECIMAL(15,2) NOT NULL,
    description VARCHAR(255),
    account_id INT NOT NULL,
    related_account_id INT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (account_id) REFERENCES accounts(id),
    FOREIGN KEY (related_account_id) REFERENCES accounts(id),
    INDEX idx_account_id (account_id),
    INDEX idx_related_account_id (related_account_id),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
```

---

*文档生成时间: 2026-04-20*
