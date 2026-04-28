"""Apple 风格全局样式"""
import streamlit as st


def inject_css():
    """注入 Apple 风格 CSS"""
    st.markdown("""
    <style>
    /* ===== Apple 风格全局 ===== */
    @import url('https://fonts.googleapis.com/css2?family=Inter:opsz,wght@14..32,400;14..32,500;14..32,600;14..32,700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'SF Pro Display', 'SF Pro Text', sans-serif;
    }

    /* 主容器 */
    .main > .block-container {
        max-width: 1100px;
        padding-top: 2rem;
        padding-bottom: 4rem;
    }

    /* ===== 标题 ===== */
    h1, h2, h3 {
        font-weight: 600 !important;
        letter-spacing: -0.02em !important;
    }
    h1 {
        font-size: 2rem !important;
        margin-bottom: 0.5rem !important;
    }
    h2 {
        font-size: 1.5rem !important;
        color: #f0f0f0 !important;
    }

    /* ===== Metric 卡片（Apple 风格）===== */
    div[data-testid="metric-container"] {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 16px;
        padding: 1rem 1.25rem;
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        transition: all 0.2s ease;
    }
    div[data-testid="metric-container"]:hover {
        background: rgba(255, 255, 255, 0.08);
        border-color: rgba(255, 255, 255, 0.12);
        transform: translateY(-1px);
    }
    div[data-testid="metric-container"] label {
        font-size: 0.8rem !important;
        font-weight: 500 !important;
        color: rgba(255, 255, 255, 0.6) !important;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    div[data-testid="metric-container"] div[data-testid="metric-value"] {
        font-size: 1.75rem !important;
        font-weight: 700 !important;
        letter-spacing: -0.02em;
    }

    /* ===== 卡片容器 ===== */
    div[data-testid="stContainer"] {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.06);
        border-radius: 16px;
        padding: 1.25rem;
        transition: border-color 0.2s ease;
    }

    /* ===== 按钮 ===== */
    .stButton button {
        border-radius: 12px !important;
        font-weight: 500 !important;
        font-size: 0.9rem !important;
        padding: 0.5rem 1.25rem !important;
        border: none !important;
        transition: all 0.2s ease !important;
    }
    .stButton button:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(0, 166, 126, 0.3);
    }
    .stButton button:active {
        transform: translateY(0);
    }
    /* 主要按钮 */
    .stButton button[kind="primary"] {
        background: linear-gradient(135deg, #00a67e 0%, #00c853 100%) !important;
        color: white !important;
    }
    /* 次要按钮 */
    .stButton button[kind="secondary"] {
        background: rgba(255, 255, 255, 0.08) !important;
        color: #e0e0e0 !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
    }
    .stButton button[kind="secondary"]:hover {
        background: rgba(255, 255, 255, 0.12) !important;
    }

    /* ===== Select / Input ===== */
    div[data-baseweb="select"] > div,
    div[data-baseweb="input"] > div,
    .stTextInput input, .stNumberInput input, .stDateInput input {
        border-radius: 12px !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        background: rgba(255, 255, 255, 0.05) !important;
        transition: all 0.2s ease;
    }
    .stTextInput input:focus, .stNumberInput input:focus, .stDateInput input:focus {
        border-color: #00a67e !important;
        box-shadow: 0 0 0 3px rgba(0, 166, 126, 0.15) !important;
    }

    /* ===== DataFrame ===== */
    div[data-testid="stDataFrame"] {
        border-radius: 12px;
        overflow: hidden;
        border: 1px solid rgba(255, 255, 255, 0.06);
    }
    div[data-testid="stDataFrame"] thead tr th {
        background: rgba(255, 255, 255, 0.05) !important;
        font-weight: 600 !important;
        font-size: 0.8rem !important;
        text-transform: uppercase;
        letter-spacing: 0.03em;
    }
    div[data-testid="stDataFrame"] tbody tr:hover {
        background: rgba(255, 255, 255, 0.03) !important;
    }

    /* ===== Sidebar ===== */
    section[data-testid="stSidebar"] {
        background: rgba(15, 18, 25, 0.95) !important;
        border-right: 1px solid rgba(255, 255, 255, 0.06);
    }
    section[data-testid="stSidebar"] .sidebar-content {
        padding: 1.5rem 1rem;
    }

    /* ===== Divider ===== */
    hr {
        border-color: rgba(255, 255, 255, 0.06) !important;
        margin: 2rem 0 !important;
    }

    /* ===== Expander ===== */
    div[data-testid="stExpander"] {
        border-radius: 16px !important;
        border: 1px solid rgba(255, 255, 255, 0.06) !important;
        background: rgba(255, 255, 255, 0.02) !important;
    }
    div[data-testid="stExpander"] summary {
        font-weight: 500 !important;
    }

    /* ===== Tabs ===== */
    button[data-baseweb="tab"] {
        border-radius: 10px !important;
        font-weight: 500 !important;
        padding: 0.5rem 1rem !important;
    }
    button[data-baseweb="tab"][aria-selected="true"] {
        background: rgba(0, 166, 126, 0.15) !important;
        color: #00a67e !important;
    }

    /* ===== Status / Toast ===== */
    div[data-testid="stStatusWidget"] {
        border-radius: 12px !important;
    }

    /* ===== Progress ===== */
    div[role="progressbar"] {
        border-radius: 10px !important;
    }

    /* ===== Radio ===== */
    label[data-baseweb="radio"] {
        border-radius: 10px;
        padding: 0.3rem 0.8rem;
        transition: background 0.2s;
    }

    /* ===== Charts (Plotly) 容器 ===== */
    .stPlotlyChart {
        border-radius: 16px;
        overflow: hidden;
    }

    /* ===== 滚动条 ===== */
    ::-webkit-scrollbar {
        width: 6px;
        height: 6px;
    }
    ::-webkit-scrollbar-track {
        background: transparent;
    }
    ::-webkit-scrollbar-thumb {
        background: rgba(255, 255, 255, 0.15);
        border-radius: 3px;
    }
    ::-webkit-scrollbar-thumb:hover {
        background: rgba(255, 255, 255, 0.25);
    }
    </style>
    """, unsafe_allow_html=True)
