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

# 通义千问API配置
DASHSCOPE_API_KEY = "sk-3e4efec26397455fa5f4dbd7e25e3c83"

# 邮件配置
EMAIL_HOST = "smtp.163.com"
EMAIL_USER = "Huibb130@163.com"
EMAIL_PASS = "YXgdqwENbHA3WhnX"
EMAIL_PORT = 25

# Ollama AI配置
OLLAMA_MODEL = "qwen:0.5b"
