import sys
import os

# 确保能找到 app 模块
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.main import app

# Vercel serverless handler
handler = app
