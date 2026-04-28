"""Apple Liquid Glass 风格全局样式"""
import streamlit as st


def inject_css():
    """注入 Apple Liquid Glass 风格 CSS"""
    st.markdown("""
    <style>
    /* ===== Font ===== */
    @import url('https://fonts.googleapis.com/css2?family=Inter:opsz,wght@14..32,300;14..32,400;14..32,500;14..32,600;14..32,700;14..32,800&display=swap');

    /* ===== Animated Gradient Background ===== */
    .stApp {
        background: linear-gradient(135deg, #0a0b0f 0%, #0f1219 30%, #13172a 60%, #0d1020 100%);
        background-attachment: fixed;
    }

    /* Subtle ambient glow */
    .stApp::before {
        content: '';
        position: fixed;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background:
            radial-gradient(ellipse 600px 400px at 20% 10%, rgba(0, 166, 126, 0.06) 0%, transparent 60%),
            radial-gradient(ellipse 500px 500px at 80% 90%, rgba(0, 100, 200, 0.04) 0%, transparent 50%);
        pointer-events: none;
        z-index: 0;
    }

    html, body, [class*="css"], .stApp, .stApp * {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'SF Pro Display', 'SF Pro Text', 'Helvetica Neue', sans-serif !important;
    }

    /* ===== Main Container ===== */
    .main > .block-container {
        max-width: 1100px;
        padding: 1.5rem 2rem 4rem;
        position: relative;
        z-index: 1;
    }

    /* ===== Typography ===== */
    h1, h2, h3 {
        font-weight: 700 !important;
        letter-spacing: -0.025em !important;
    }
    h1 {
        font-size: 2.25rem !important;
        margin-bottom: 0.25rem !important;
        background: linear-gradient(135deg, #ffffff 0%, #a0a8c0 100%);
        -webkit-background-clip: text !important;
        -webkit-text-fill-color: transparent !important;
        background-clip: text !important;
    }
    h2 {
        font-size: 1.5rem !important;
        color: #e8ecf4 !important;
        font-weight: 600 !important;
        margin-top: 0.5rem !important;
    }
    h3 {
        font-size: 1.15rem !important;
        color: #d0d4e0 !important;
    }

    /* ===== Liquid Glass Metric Cards ===== */
    div[data-testid="metric-container"] {
        background: rgba(255, 255, 255, 0.04);
        border: 1px solid rgba(255, 255, 255, 0.06);
        border-radius: 20px;
        padding: 1.25rem 1.5rem;
        backdrop-filter: blur(40px) saturate(150%);
        -webkit-backdrop-filter: blur(40px) saturate(150%);
        box-shadow:
            0 4px 24px rgba(0, 0, 0, 0.2),
            inset 0 1px 0 rgba(255, 255, 255, 0.06);
        transition: all 0.3s cubic-bezier(0.25, 0.46, 0.45, 0.94);
    }
    div[data-testid="metric-container"]:hover {
        background: rgba(255, 255, 255, 0.07);
        border-color: rgba(255, 255, 255, 0.1);
        transform: translateY(-2px);
        box-shadow:
            0 8px 32px rgba(0, 0, 0, 0.3),
            inset 0 1px 0 rgba(255, 255, 255, 0.08);
    }
    div[data-testid="metric-container"] label {
        font-size: 0.75rem !important;
        font-weight: 500 !important;
        color: rgba(255, 255, 255, 0.45) !important;
        text-transform: uppercase;
        letter-spacing: 0.08em;
    }
    div[data-testid="metric-container"] div[data-testid="metric-value"] {
        font-size: 1.8rem !important;
        font-weight: 700 !important;
        letter-spacing: -0.03em;
        color: #f0f4ff !important;
    }

    /* ===== Liquid Glass Containers ===== */
    div[data-testid="stContainer"], .stColumn > div[data-testid="stVerticalBlock"] > div[data-testid="element-container"] > div {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-radius: 20px;
        padding: 1.25rem;
        backdrop-filter: blur(30px) saturate(150%);
        -webkit-backdrop-filter: blur(30px) saturate(150%);
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
        transition: all 0.3s ease;
    }

    /* Card containers (used in OCR import list) */
    section[data-testid="stMain"] div[data-testid="stVerticalBlock"] > div.element-container > div[data-testid="stMarkdownContainer"] + div,
    div[data-testid="stVerticalBlock"] > div[data-testid="element-container"] > div[data-testid="stContainer"] {
        background: rgba(255, 255, 255, 0.03) !important;
        border: 1px solid rgba(255, 255, 255, 0.06) !important;
        border-radius: 20px !important;
        padding: 1.25rem !important;
        backdrop-filter: blur(30px) saturate(150%);
        -webkit-backdrop-filter: blur(30px) saturate(150%);
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
    }

    /* ===== Buttons ===== */
    .stButton button {
        border-radius: 14px !important;
        font-weight: 500 !important;
        font-size: 0.9rem !important;
        padding: 0.6rem 1.5rem !important;
        border: none !important;
        letter-spacing: 0.01em !important;
        transition: all 0.3s cubic-bezier(0.25, 0.46, 0.45, 0.94) !important;
    }
    .stButton button:hover {
        transform: translateY(-1px);
    }
    .stButton button:active {
        transform: translateY(0) scale(0.98);
    }

    /* Primary button — Apple-style gradient */
    .stButton button[kind="primary"] {
        background: linear-gradient(135deg, #00a67e 0%, #00856a 100%) !important;
        color: white !important;
        box-shadow: 0 4px 16px rgba(0, 166, 126, 0.25) !important;
    }
    .stButton button[kind="primary"]:hover {
        box-shadow: 0 6px 24px rgba(0, 166, 126, 0.35) !important;
        background: linear-gradient(135deg, #00b889 0%, #009675 100%) !important;
    }

    /* Secondary button */
    .stButton button[kind="secondary"] {
        background: rgba(255, 255, 255, 0.06) !important;
        color: #c8ccd8 !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        backdrop-filter: blur(10px);
    }
    .stButton button[kind="secondary"]:hover {
        background: rgba(255, 255, 255, 0.1) !important;
        border-color: rgba(255, 255, 255, 0.12) !important;
    }

    /* ===== Text Input / Select / Number Input ===== */
    div[data-baseweb="select"] > div,
    div[data-baseweb="input"] > div,
    .stTextInput input, .stNumberInput input, .stDateInput input, .stTextArea textarea {
        border-radius: 14px !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        background: rgba(255, 255, 255, 0.04) !important;
        color: #e8ecf4 !important;
        padding: 0.6rem 1rem !important;
        backdrop-filter: blur(10px);
        transition: all 0.25s ease;
    }
    .stTextInput input:focus, .stNumberInput input:focus,
    .stDateInput input:focus, .stTextArea textarea:focus {
        border-color: rgba(0, 166, 126, 0.5) !important;
        background: rgba(255, 255, 255, 0.06) !important;
        box-shadow: 0 0 0 4px rgba(0, 166, 126, 0.08) !important;
    }
    .stTextInput input::placeholder, .stNumberInput input::placeholder {
        color: rgba(255, 255, 255, 0.25) !important;
    }

    /* ===== Select / Dropdown ===== */
    div[data-baseweb="select"] > div {
        min-height: 2.8rem;
    }
    div[data-baseweb="select"] > div:hover {
        border-color: rgba(255, 255, 255, 0.15) !important;
    }

    /* ===== DataFrame ===== */
    div[data-testid="stDataFrame"] {
        border-radius: 16px;
        overflow: hidden;
        border: 1px solid rgba(255, 255, 255, 0.06);
        background: rgba(255, 255, 255, 0.02);
    }
    div[data-testid="stDataFrame"] thead tr th {
        background: rgba(255, 255, 255, 0.04) !important;
        font-weight: 600 !important;
        font-size: 0.75rem !important;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        color: rgba(255, 255, 255, 0.5) !important;
        padding: 0.8rem 1rem !important;
        border-bottom: 1px solid rgba(255, 255, 255, 0.06) !important;
    }
    div[data-testid="stDataFrame"] tbody tr {
        border-bottom: 1px solid rgba(255, 255, 255, 0.03) !important;
        transition: background 0.2s;
    }
    div[data-testid="stDataFrame"] tbody tr:hover {
        background: rgba(255, 255, 255, 0.04) !important;
    }
    div[data-testid="stDataFrame"] tbody td {
        padding: 0.7rem 1rem !important;
        color: #c8ccd8 !important;
    }

    /* ===== Sidebar ===== */
    section[data-testid="stSidebar"] {
        background: rgba(10, 12, 18, 0.95) !important;
        border-right: 1px solid rgba(255, 255, 255, 0.04);
        backdrop-filter: blur(40px) saturate(150%);
        -webkit-backdrop-filter: blur(40px) saturate(150%);
    }
    section[data-testid="stSidebar"] .sidebar-content {
        padding: 1.5rem 1rem;
    }
    section[data-testid="stSidebar"] .stButton button {
        width: 100%;
        text-align: left;
        padding: 0.5rem 1rem !important;
        background: transparent !important;
        border: none !important;
        color: rgba(255, 255, 255, 0.6) !important;
        font-weight: 400 !important;
        border-radius: 10px !important;
    }
    section[data-testid="stSidebar"] .stButton button:hover {
        background: rgba(255, 255, 255, 0.05) !important;
        color: rgba(255, 255, 255, 0.9) !important;
    }

    /* ===== Expander ===== */
    div[data-testid="stExpander"] {
        border-radius: 20px !important;
        border: 1px solid rgba(255, 255, 255, 0.06) !important;
        background: rgba(255, 255, 255, 0.02) !important;
        backdrop-filter: blur(20px);
        box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
        overflow: hidden;
    }
    div[data-testid="stExpander"] summary {
        font-weight: 500 !important;
        padding: 0.8rem 1rem !important;
        border-radius: 20px !important;
    }
    div[data-testid="stExpander"] summary:hover {
        background: rgba(255, 255, 255, 0.03);
    }
    div[data-testid="stExpander"] div[role="button"] p {
        font-size: 1rem !important;
    }

    /* ===== Tabs ===== */
    button[data-baseweb="tab"] {
        border-radius: 12px !important;
        font-weight: 500 !important;
        padding: 0.5rem 1.2rem !important;
        color: rgba(255, 255, 255, 0.5) !important;
        transition: all 0.2s ease !important;
        border: none !important;
    }
    button[data-baseweb="tab"]:hover {
        color: rgba(255, 255, 255, 0.8) !important;
        background: rgba(255, 255, 255, 0.04) !important;
    }
    button[data-baseweb="tab"][aria-selected="true"] {
        background: rgba(0, 166, 126, 0.12) !important;
        color: #00a67e !important;
    }

    /* ===== Divider ===== */
    hr {
        border-color: rgba(255, 255, 255, 0.04) !important;
        margin: 1.5rem 0 !important;
        border-width: 0.5px !important;
    }

    /* ===== Status Messages ===== */
    div[data-testid="stStatusWidget"] {
        border-radius: 16px !important;
        border: 1px solid rgba(255, 255, 255, 0.06) !important;
        backdrop-filter: blur(10px);
    }
    .stAlert {
        border-radius: 16px !important;
        border: 1px solid rgba(255, 255, 255, 0.06) !important;
        backdrop-filter: blur(10px);
        background: rgba(255, 255, 255, 0.03) !important;
    }
    .stAlert[data-baseweb="notification"] {
        border-radius: 16px !important;
    }

    /* Success / Error / Info blocks */
    div[data-testid="stAlertContainer"] > div {
        border-radius: 16px !important;
        border: 1px solid rgba(255, 255, 255, 0.06) !important;
    }
    .st-bd, .st-be, .st-bf, .st-bg {
        border-radius: 16px !important;
    }

    /* ===== Progress Bar ===== */
    div[role="progressbar"] {
        border-radius: 20px !important;
        background: rgba(255, 255, 255, 0.06) !important;
    }
    div[role="progressbar"] > div {
        background: linear-gradient(90deg, #00a67e, #00c853) !important;
        border-radius: 20px !important;
    }

    /* ===== Radio ===== */
    label[data-baseweb="radio"] {
        border-radius: 12px;
        padding: 0.4rem 1rem;
        transition: all 0.2s;
        background: rgba(255, 255, 255, 0.02);
        border: 1px solid transparent;
    }
    label[data-baseweb="radio"]:hover {
        background: rgba(255, 255, 255, 0.05);
        border-color: rgba(255, 255, 255, 0.06);
    }
    label[data-baseweb="radio"][aria-checked="true"] {
        background: rgba(0, 166, 126, 0.1);
        border-color: rgba(0, 166, 126, 0.2);
    }

    /* ===== Plotly Chart Containers ===== */
    .stPlotlyChart {
        border-radius: 20px;
        overflow: hidden;
        background: rgba(255, 255, 255, 0.02);
        border: 1px solid rgba(255, 255, 255, 0.04);
        padding: 0.5rem;
    }

    /* ===== Toast ===== */
    div[data-testid="stToast"] {
        border-radius: 16px !important;
        backdrop-filter: blur(30px);
        background: rgba(10, 12, 18, 0.9) !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
    }

    /* ===== Scrollbar ===== */
    ::-webkit-scrollbar { width: 5px; height: 5px; }
    ::-webkit-scrollbar-track { background: transparent; }
    ::-webkit-scrollbar-thumb {
        background: rgba(255, 255, 255, 0.08);
        border-radius: 3px;
    }
    ::-webkit-scrollbar-thumb:hover { background: rgba(255, 255, 255, 0.15); }

    /* ===== Spinner ===== */
    div[data-testid="stSpinner"] {
        border-radius: 16px;
    }

    /* ===== Checkbox ===== */
    label[data-baseweb="checkbox"] {
        border-radius: 6px;
    }

    /* ===== Date Input ===== */
    div[data-testid="stDateInput"] > div {
        border-radius: 14px !important;
    }

    /* ===== File Uploader ===== */
    section[data-testid="stFileUploader"] {
        border-radius: 20px !important;
        border: 1px dashed rgba(255, 255, 255, 0.1) !important;
        background: rgba(255, 255, 255, 0.02) !important;
        padding: 1rem !important;
    }
    section[data-testid="stFileUploader"]:hover {
        border-color: rgba(0, 166, 126, 0.3) !important;
        background: rgba(0, 166, 126, 0.03) !important;
    }

    /* ===== Info/Warning/Success/Error boxes ===== */
    .stInfo, .stWarning, .stSuccess, .stError {
        border-radius: 16px !important;
        border: 1px solid rgba(255, 255, 255, 0.06) !important;
        backdrop-filter: blur(10px);
        padding: 1rem 1.25rem !important;
    }
    .stInfo {
        background: rgba(0, 122, 255, 0.06) !important;
        border-color: rgba(0, 122, 255, 0.12) !important;
    }
    .stWarning {
        background: rgba(255, 204, 0, 0.06) !important;
        border-color: rgba(255, 204, 0, 0.12) !important;
    }
    .stSuccess {
        background: rgba(0, 166, 126, 0.06) !important;
        border-color: rgba(0, 166, 126, 0.12) !important;
    }

    /* ===== Column gap refinement ===== */
    div[data-testid="column"] {
        gap: 1.5rem !important;
    }

    /* ===== Multi-select / searchable ===== */
    div[data-baseweb="multi-select"] > div {
        border-radius: 14px !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        background: rgba(255, 255, 255, 0.04) !important;
        min-height: 2.8rem !important;
    }
    div[data-baseweb="multi-select"] > div:hover {
        border-color: rgba(255, 255, 255, 0.15) !important;
    }
    </style>
    """, unsafe_allow_html=True)
