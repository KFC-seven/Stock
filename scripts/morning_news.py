"""新闻抓取脚本 - 由 GitHub Actions 调用（Phase 3 实现）"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from src.database import init_db, get_session, NewsKeyword, NewsCache
from datetime import date

# 后续 Phase 3 接入新闻 API + DeepSeek 分析
# 当前版本仅占位，保证 workflow 不报错


def main():
    init_db()
    print("新闻推送功能将在后续版本实现")
    print("（计划：集成免费新闻API + DeepSeek 投资建议）")


if __name__ == "__main__":
    main()
