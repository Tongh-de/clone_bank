"""
配置文件
"""
import os

# 数据库配置
DATABASE_URL = "mysql+pymysql://root:123456@localhost:3306/bank_db"

# JWT配置
SECRET_KEY = "your-secret-key-change-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

# 银行配置
BANK_NAME = "演示银行"
CURRENCY = "CNY"

# 分页配置
PAGE_SIZE = 20

# 报表配置
REPORT_DIR = "reports"

# 通义千问API配置（请替换为你的密钥）
DASHSCOPE_API_KEY = "sk-3e4efec26397455fa5f4dbd7e25e3c83"
