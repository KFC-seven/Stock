"""启动脚本 - 运行投资管家"""
import os
import sys

# 确保项目根目录在 Python 路径中
sys.path.insert(0, os.path.dirname(__file__))

if __name__ == "__main__":
    os.system("streamlit run app.py")
