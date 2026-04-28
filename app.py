"""投资管家 - 个人投资管理系统"""
import streamlit as st
from src.database import init_db
from src.auth import login_page

# 页面配置（必须放在最前面）
st.set_page_config(
    page_title="投资管家",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# 初始化数据库
init_db()


def main():
    """主入口"""
    # 先登录
    login_page()

    # 未登录不继续
    if not st.session_state.get("authentication_status"):
        # 清除侧边栏
        st.sidebar.empty()
        return

    # 已登录 - 侧边栏显示用户信息
    user_name = st.session_state.get("name", "用户")
    with st.sidebar:
        st.markdown(f"### 👋 {user_name}")
        st.divider()

    # 页面路由 - 使用 pages 目录自动路由
    st.switch_page("pages/01_📊_看板.py")


if __name__ == "__main__":
    main()
