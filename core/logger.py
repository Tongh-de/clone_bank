"""
日志配置模块
"""
import logging
import os
from logging.handlers import RotatingFileHandler
from datetime import datetime

# 日志目录
LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)

# 日志格式
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

# 日志级别
LOG_LEVEL = logging.INFO


def get_logger(name: str) -> logging.Logger:
    """
    获取日志记录器
    """
    logger = logging.getLogger(name)
    
    if logger.handlers:
        return logger
    
    logger.setLevel(LOG_LEVEL)
    
    # 控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setLevel(LOG_LEVEL)
    console_formatter = logging.Formatter(LOG_FORMAT, DATE_FORMAT)
    console_handler.setFormatter(console_formatter)
    
    # 文件处理器
    today = datetime.now().strftime("%Y-%m-%d")
    
    file_handler = RotatingFileHandler(
        os.path.join(LOG_DIR, f"app_{today}.log"),
        maxBytes=10*1024*1024,
        backupCount=30,
        encoding="utf-8"
    )
    file_handler.setLevel(LOG_LEVEL)
    file_formatter = logging.Formatter(LOG_FORMAT, DATE_FORMAT)
    file_handler.setFormatter(file_formatter)
    
    # 错误日志
    error_handler = RotatingFileHandler(
        os.path.join(LOG_DIR, f"error_{today}.log"),
        maxBytes=10*1024*1024,
        backupCount=30,
        encoding="utf-8"
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(file_formatter)
    
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    logger.addHandler(error_handler)
    
    return logger


# 预定义日志记录器
app_logger = get_logger("bank_app")
user_logger = get_logger("bank_user")
transaction_logger = get_logger("bank_transaction")
ai_logger = get_logger("bank_ai")
api_logger = get_logger("bank_api")
db_logger = get_logger("bank_db")


def log_user_action(username: str, action: str, details: str = "", ip: str = ""):
    """记录用户操作"""
    ip_info = f" [IP: {ip}]" if ip else ""
    user_logger.info(f"[{username}] {action}{ip_info} - {details}")


def log_transaction(account_number: str, action: str, amount: float, balance: float, result: str):
    """记录交易操作"""
    transaction_logger.info(f"[{account_number}] {action}: ¥{amount:.2f}, 余额: ¥{balance:.2f}, 结果: {result}")


def log_ai_request(user: str, message: str, method: str, success: bool):
    """记录AI请求"""
    status = "成功" if success else "失败"
    ai_logger.info(f"[{user}] {method}: {message[:50]}... - {status}")


def log_api_request(method: str, path: str, user: str, status_code: int, duration: float):
    """记录API请求"""
    api_logger.info(f"{method} {path} - 用户: {user} - 状态: {status_code} - 耗时: {duration:.3f}s")


def log_error(module: str, error: Exception, details: str = ""):
    """记录错误"""
    detail_info = f" - {details}" if details else ""
    app_logger.error(f"[{module}] {type(error).__name__}: {str(error)}{detail_info}", exc_info=True)
