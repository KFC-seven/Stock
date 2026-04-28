"""FastAPI 配置"""
import os
from datetime import timedelta

# 项目路径
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))

# JWT
SECRET_KEY = os.getenv("SECRET_KEY", "stock-invest-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE = timedelta(days=30)

# 数据库
_db_dir = os.path.join(BASE_DIR, "data")
os.makedirs(_db_dir, exist_ok=True)
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    f"sqlite:///{os.path.join(_db_dir, 'investments.db')}"
)

# CORS
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:5173,http://localhost:3000").split(",")
