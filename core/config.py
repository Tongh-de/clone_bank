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
DASHSCOPE_API_KEY = "sk-62c0f5ff0ebc4f93aca0f640db2f5287"

# 邮件配置
EMAIL_HOST = "smtp.163.com"
EMAIL_USER = "Huibb130@163.com"
EMAIL_PASS = "YXgdqwENbHA3WhnX"
EMAIL_PORT = 25

# Ollama AI配置
OLLAMA_MODEL = "qwen:0.5b"

# 高德地图配置
AMAP_WEB_KEY = "ca7a8b8dd6c21ae7226306dc7488193d"  # 前端使用
AMAP_SERVER_KEY = "750b030020ccffe9e66e365563c1abbd"  # 后端使用
