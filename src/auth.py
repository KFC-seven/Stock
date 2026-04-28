import os
import yaml
import bcrypt
import streamlit as st
import streamlit_authenticator as stauth
from src.database import get_session, User

CONFIG_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".auth_config.yaml")


def _load_config():
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)
    return {"credentials": {"usernames": {}}, "cookie": {
        "expiry_days": 30,
        "key": "stock_invest",
        "name": "stock_auth"
    }, "preauthorized": {"emails": []}}


def _save_config(config):
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        yaml.dump(config, f, allow_unicode=True)


def register_user(username, password, display_name):
    """注册新用户"""
    config = _load_config()
    if username in config["credentials"]["usernames"]:
        return False, "用户名已存在"

    hashed = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
    config["credentials"]["usernames"][username] = {
        "email": f"{username}@local",
        "name": display_name,
        "password": hashed,
    }
    _save_config(config)

    # 同步写入数据库
    db = get_session()
    try:
        existing = db.query(User).filter(User.username == username).first()
        if not existing:
            user = User(username=username, password_hash=hashed, display_name=display_name)
            db.add(user)
            db.commit()
    finally:
        db.close()
    return True, "注册成功"


def get_authenticator():
    """获取 authenticator 实例"""
    config = _load_config()
    authenticator = stauth.Authenticate(
        config["credentials"],
        config["cookie"]["name"],
        config["cookie"]["key"],
        config["cookie"]["expiry_days"],
        auto_hash=False,  # 我们手动 hash 密码
    )
    return authenticator


def login_page():
    """渲染登录页面，返回登录状态"""
    # 确保数据库有用户同步
    _sync_users_from_config()

    authenticator = get_authenticator()
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.title("📊 投资管家")

        tab1, tab2 = st.tabs(["登录", "注册"])
        with tab1:
            authenticator.login(location="main", fields={
                "Form name": "登录",
                "Username": "用户名",
                "Password": "密码",
                "Login": "登录"
            })

        with tab2:
            with st.form("register_form"):
                new_user = st.text_input("用户名", placeholder="请输入用户名")
                new_name = st.text_input("显示名称", placeholder="你的昵称")
                new_pass = st.text_input("密码", type="password", placeholder="请输入密码")
                new_pass2 = st.text_input("确认密码", type="password", placeholder="再次输入密码")
                submitted = st.form_submit_button("注册", use_container_width=True)
                if submitted:
                    if not new_user or not new_name or not new_pass:
                        st.error("请填写完整信息")
                    elif new_pass != new_pass2:
                        st.error("两次密码不一致")
                    else:
                        ok, msg = register_user(new_user, new_pass, new_name)
                        if ok:
                            # 注册后自动登录
                            st.session_state["authentication_status"] = True
                            st.session_state["username"] = new_user
                            st.session_state["name"] = new_name
                            st.rerun()
                        else:
                            st.error(msg)

        if st.session_state.get("authentication_status"):
            # 确保 session 中有 user_id
            if "user_id" not in st.session_state:
                username = st.session_state.get("username")
                if username:
                    db = get_session()
                    try:
                        user = db.query(User).filter(User.username == username).first()
                        if user:
                            st.session_state["user_id"] = user.id
                    finally:
                        db.close()
            authenticator.logout("退出登录", "sidebar")


def _sync_users_from_config():
    """确保配置中的用户同步到数据库"""
    config = _load_config()
    db = get_session()
    try:
        for username, info in config["credentials"]["usernames"].items():
            existing = db.query(User).filter(User.username == username).first()
            if not existing:
                user = User(
                    username=username,
                    password_hash=info["password"],
                    display_name=info.get("name", username),
                )
                db.add(user)
        db.commit()
    finally:
        db.close()


def ensure_auth():
    """在页面加载时验证 cookie 并确保登录状态。

    所有受保护的页面在开头调用此函数。
    如果 cookie 有效，自动恢复登录状态；否则显示登录页。
    """
    _sync_users_from_config()
    authenticator = get_authenticator()

    # unrendered 模式：只检查 cookie，不渲染表单
    authenticator.login(location="unrendered")

    # 如果 cookie 恢复了登录，确保 user_id 存在
    if st.session_state.get("authentication_status"):
        if "user_id" not in st.session_state:
            username = st.session_state.get("username")
            if username:
                db = get_session()
                try:
                    user = db.query(User).filter(User.username == username).first()
                    if user:
                        st.session_state["user_id"] = user.id
                finally:
                    db.close()

    # 未登录则显示登录页并停止
    if not st.session_state.get("authentication_status"):
        login_page()
        st.stop()
