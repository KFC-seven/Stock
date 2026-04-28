"""设置 - 个人信息、关键词配置"""
import streamlit as st
from src.database import get_session, NewsKeyword
from src.styles import inject_css
from src.auth import ensure_auth

st.set_page_config(page_title="设置", page_icon="⚙️", layout="wide")
inject_css()

ensure_auth()

user_id = st.session_state.get("user_id")
user_name = st.session_state.get("name", "用户")

st.title("⚙️ 设置")

# 个人信息
with st.container(border=True):
    st.subheader("👤 个人信息")
    st.write(f"用户名: {st.session_state.get('username', '')}")
    st.write(f"显示名称: {user_name}")
    st.caption("修改密码功能即将上线")

# 新闻关键词设置
st.divider()
with st.container(border=True):
    st.subheader("📰 新闻关键词")
    st.caption("设置你关注的关键词，系统每天早8点推送相关新闻和投资建议")

    db = get_session()
    try:
        keywords = db.query(NewsKeyword).filter(
            NewsKeyword.user_id == user_id,
            NewsKeyword.is_active == True
        ).all()

        if keywords:
            st.write("当前关键词：")
            for kw in keywords:
                c1, c2 = st.columns([4, 1])
                with c1:
                    st.markdown(f"- {kw.keyword}")
                with c2:
                    if st.button("删除", key=f"del_kw_{kw.id}", use_container_width=True):
                        kw.is_active = False
                        db.commit()
                        st.toast(f"已删除关键词: {kw.keyword}", icon="🗑️")
                        st.rerun()
        else:
            st.info("还没有设置关键词")

        # 添加新关键词
        with st.form("add_keyword_form"):
            new_keyword = st.text_input("添加关键词", placeholder="如: 新能源、半导体、消费...")
            if st.form_submit_button("添加", use_container_width=True):
                if new_keyword.strip():
                    kw = NewsKeyword(
                        user_id=user_id,
                        keyword=new_keyword.strip(),
                    )
                    db.add(kw)
                    db.commit()
                    st.success(f"已添加关键词: {new_keyword}")
                    st.rerun()
    finally:
        db.close()

# 关于
st.divider()
with st.container(border=True):
    st.subheader("ℹ️ 关于")
    st.markdown("""
    **投资管家 v1.0**
    - 数据来源：AKShare（东方财富/新浪财经）
    - 数据仅供个人参考，不构成投资建议
    - 投资有风险，入市需谨慎
    """)
