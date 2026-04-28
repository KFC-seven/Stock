"""投资管家 - 个人投资管理系统"""
import streamlit as st
from src.database import init_db
from src.auth import login_page
from src.styles import inject_css

# 页面配置（必须放在最前面）
st.set_page_config(
    page_title="投资管家",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# 初始化数据库
init_db()

# 全局 CSS（仅注入一次）
if "_css_injected" not in st.session_state:
    inject_css()
    st.session_state._css_injected = True


def main():
    """主入口"""
    # 验证登录（cookie 自动续登 or 显示登录页）
    ensure_auth()

    # 已登录 - 侧边栏显示用户信息
    user_name = st.session_state.get("name", "用户")
    with st.sidebar:
        st.markdown(f"### 👋 {user_name}")
        st.divider()

    # 跳转到看板
    st.switch_page("pages/01_📊_看板.py")


if __name__ == "__main__":
    main()
