-- =============================================
-- 银行账户管理系统 - MySQL 数据库初始化脚本
-- =============================================

-- 创建数据库
CREATE DATABASE IF NOT EXISTS bank_db DEFAULT CHARSET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE bank_db;

-- =============================================
-- 用户表
-- =============================================
CREATE TABLE IF NOT EXISTS `users` (
    `id` INT PRIMARY KEY AUTO_INCREMENT,
    `username` VARCHAR(50) NOT NULL UNIQUE,
    `password_hash` VARCHAR(255) NOT NULL,
    `full_name` VARCHAR(100) NOT NULL,
    `email` VARCHAR(100) UNIQUE,
    `role` VARCHAR(20) DEFAULT 'user',
    `is_active` BOOLEAN DEFAULT TRUE,
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
    `last_login` DATETIME,
    INDEX `idx_username` (`username`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- =============================================
-- 账户表
-- =============================================
CREATE TABLE IF NOT EXISTS `accounts` (
    `id` INT PRIMARY KEY AUTO_INCREMENT,
    `account_number` VARCHAR(20) NOT NULL UNIQUE,
    `account_type` VARCHAR(20) DEFAULT 'savings',
    `balance` DECIMAL(15,2) DEFAULT 0.00,
    `status` VARCHAR(20) DEFAULT 'active',
    `owner_id` INT NOT NULL,
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
    `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (`owner_id`) REFERENCES `users`(`id`) ON DELETE CASCADE,
    INDEX `idx_account_number` (`account_number`),
    INDEX `idx_owner_id` (`owner_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- =============================================
-- 交易记录表
-- =============================================
CREATE TABLE IF NOT EXISTS `transactions` (
    `id` INT PRIMARY KEY AUTO_INCREMENT,
    `transaction_type` VARCHAR(20) NOT NULL,
    `amount` DECIMAL(15,2) NOT NULL,
    `balance_before` DECIMAL(15,2) NOT NULL,
    `balance_after` DECIMAL(15,2) NOT NULL,
    `description` VARCHAR(255),
    `account_id` INT NOT NULL,
    `related_account_id` INT,
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (`account_id`) REFERENCES `accounts`(`id`) ON DELETE CASCADE,
    FOREIGN KEY (`related_account_id`) REFERENCES `accounts`(`id`) ON DELETE SET NULL,
    INDEX `idx_account_id` (`account_id`),
    INDEX `idx_created_at` (`created_at`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- =============================================
-- 示例数据
-- =============================================

-- 插入用户 (密码都是: 123456)
-- bcrypt hash for "123456": $2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/X4d5GIHwcWuPMx5Wy
INSERT INTO `users` (`username`, `password_hash`, `full_name`, `email`, `role`, `is_active`, `created_at`) VALUES
('admin', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/X4d5GIHwcWuPMx5Wy', '系统管理员', 'admin@bank.com', 'admin', TRUE, NOW()),
('zhangsan', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/X4d5GIHwcWuPMx5Wy', '张三', 'zhangsan@example.com', 'user', TRUE, NOW()),
('lisi', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/X4d5GIHwcWuPMx5Wy', '李四', 'lisi@example.com', 'user', TRUE, NOW()),
('wangwu', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/X4d5GIHwcWuPMx5Wy', '王五', 'wangwu@example.com', 'user', TRUE, NOW());

-- 插入账户
INSERT INTO `accounts` (`account_number`, `account_type`, `balance`, `status`, `owner_id`, `created_at`) VALUES
('622800000001', 'savings', 50000.00, 'active', 2, '2024-01-15 10:30:00'),
('622800000002', 'checking', 25000.00, 'active', 2, '2024-02-20 14:20:00'),
('622800000003', 'savings', 80000.00, 'active', 3, '2024-01-10 09:15:00'),
('622800000004', 'savings', 35000.00, 'active', 4, '2024-03-05 16:45:00'),
('622800000005', 'savings', 10000.00, 'frozen', 2, '2023-11-20 11:00:00');

-- 插入交易记录
INSERT INTO `transactions` (`transaction_type`, `amount`, `balance_before`, `balance_after`, `description`, `account_id`, `created_at`) VALUES
-- 张三 储蓄账户交易
('deposit', 10000.00, 0.00, 10000.00, '开户存款', 1, '2024-01-15 10:35:00'),
('deposit', 20000.00, 10000.00, 30000.00, '工资入账', 1, '2024-01-31 09:00:00'),
('withdraw', 5000.00, 30000.00, 25000.00, '日常消费', 1, '2024-02-10 15:30:00'),
('transfer_in', 30000.00, 25000.00, 55000.00, '转账来自 王五', 1, '2024-02-15 10:00:00'),
('transfer_out', 5000.00, 55000.00, 50000.00, '转账至 李四', 1, '2024-03-01 14:20:00'),

-- 张三 支票账户交易
('deposit', 25000.00, 0.00, 25000.00, '开户存款', 2, '2024-02-20 14:25:00'),
('withdraw', 8000.00, 25000.00, 17000.00, '支付货款', 2, '2024-03-05 11:00:00'),
('withdraw', 2000.00, 17000.00, 15000.00, '还款', 2, '2024-03-10 16:00:00'),

-- 李四 账户交易
('deposit', 50000.00, 0.00, 50000.00, '开户存款', 3, '2024-01-10 09:20:00'),
('deposit', 40000.00, 50000.00, 90000.00, '理财赎回', 3, '2024-01-25 10:30:00'),
('withdraw', 10000.00, 90000.00, 80000.00, '购买家电', 3, '2024-02-01 14:00:00'),
('transfer_in', 5000.00, 80000.00, 85000.00, '转账来自 张三', 3, '2024-03-01 14:25:00'),

-- 王五 账户交易
('deposit', 20000.00, 0.00, 20000.00, '开户存款', 4, '2024-03-05 16:50:00'),
('deposit', 25000.00, 20000.00, 45000.00, '奖金入账', 4, '2024-03-10 09:00:00'),
('transfer_out', 10000.00, 45000.00, 35000.00, '转账至 张三', 4, '2024-02-15 10:05:00'),

-- 张三 冻结账户
('deposit', 10000.00, 0.00, 10000.00, '开户存款', 5, '2023-11-20 11:05:00'),
('withdraw', 5000.00, 10000.00, 5000.00, '取款', 5, '2023-12-01 10:00:00');

-- =============================================
-- 数据验证
-- =============================================
SELECT '用户数据:' AS '';
SELECT id, username, full_name, role FROM users;

SELECT '账户数据:' AS '';
SELECT a.account_number, a.account_type, a.balance, a.status, u.full_name 
FROM accounts a 
JOIN users u ON a.owner_id = u.id;

SELECT '交易统计:' AS '';
SELECT COUNT(*) as 总交易数 FROM transactions;
SELECT SUM(amount) as 总交易金额 FROM transactions WHERE transaction_type = 'deposit';
