"""每日净值更新脚本 - 由 GitHub Actions 调用"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from src.database import init_db, get_session, Holding
from src.data_provider import update_all_prices


def main():
    init_db()
    db = get_session()
    try:
        holdings = db.query(Holding).all()
        if not holdings:
            print("没有持仓记录，跳过更新")
            return

        print(f"开始更新 {len(holdings)} 条持仓的净值...")
        results = update_all_prices(holdings)

        success = sum(1 for r in results if r[3])
        fail = sum(1 for r in results if not r[3])
        print(f"更新完成：成功 {success}，失败 {fail}")

        if fail > 0:
            print("失败的资产：")
            for r in results:
                if not r[3]:
                    print(f"  - {r[0]} ({r[1]})")
    finally:
        db.close()


if __name__ == "__main__":
    main()
