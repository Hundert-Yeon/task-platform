import streamlit as st
from pages_modules import dashboard, taskboard, calendar_view, files_view, memo_view, admin_view, shared_feed
from utils.state import init_state
from utils.auth import login_screen

# ── 페이지 설정 ──────────────────────────────────────────────
st.set_page_config(
    page_title="영업기획팀 · 업무관리 시스템",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── 전역 CSS ─────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;400;500;600;700&family=DM+Mono:wght@400;500&display=swap');

:root {
  --bg: #f0f2f7;
  --surface: #ffffff;
  --surface2: #f8fafc;
  --blue: #1d4ed8;
  --blue-light: #eff6ff;
  --blue-sky: #dbeafe;
  --ink: #111827;
  --ink-mid: #374151;
  --ink-light: #6b7280;
  --ink-ghost: #d1d5db;
  --border: #e5e7eb;
  --green: #059669;
  --amber: #d97706;
  --red: #dc2626;
}

/* ── 전체 앱 배경 ── */
html, body { font-family: 'Noto Sans KR', sans-serif; }
.stApp,
[data-testid="stAppViewContainer"],
[data-testid="stHeader"] {
  background: var(--bg) !important;
}
.main .block-container {
  background: var(--bg);
  padding-top: 1.5rem;
  padding-bottom: 2rem;
}

/* Streamlit 기본 UI 일부 숨김 */
#MainMenu { visibility: hidden; }
[data-testid="stToolbar"] { display: none; }
footer { visibility: hidden; }

/* ── 사이드바: 흰색 배경 + 어두운 텍스트 ── */
[data-testid="stSidebar"],
[data-testid="stSidebarContent"],
div[data-testid="stSidebarContent"],
section[data-testid="stSidebar"] > div:first-child {
  background: var(--surface) !important;
  background-color: var(--surface) !important;
}
section[data-testid="stSidebar"] {
  border-right: 1px solid var(--border) !important;
  box-shadow: 1px 0 6px rgba(0,0,0,0.04) !important;
}

/* 사이드바 텍스트 기본색 = 어두운 회색 */
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] small,
[data-testid="stSidebar"] div[data-testid="stCaptionContainer"],
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {
  color: var(--ink-light) !important;
}
[data-testid="stSidebar"] hr {
  border-color: var(--border) !important;
  margin: 6px 0 !important;
}

/* ── 사이드바 네비게이션 버튼 (비활성) ── */
[data-testid="stSidebar"] button,
[data-testid="stSidebar"] button[data-testid="baseButton-secondary"],
[data-testid="stSidebar"] [data-testid="stBaseButton-secondary"] {
  background: transparent !important;
  border: none !important;
  border-left: 3px solid transparent !important;
  border-radius: 7px !important;
  text-align: left !important;
  color: var(--ink-light) !important;
  padding: 8px 9px !important;
  font-size: 13px !important;
  font-weight: 500 !important;
  margin: 1px 0 !important;
  box-shadow: none !important;
  font-family: 'Noto Sans KR', sans-serif !important;
  transition: background 0.11s, color 0.11s !important;
}
[data-testid="stSidebar"] button:hover {
  background: var(--bg) !important;
  color: var(--ink) !important;
  border-left-color: var(--ink-ghost) !important;
}
/* ── 사이드바 활성 버튼 ── */
[data-testid="stSidebar"] button[data-testid="baseButton-primary"],
[data-testid="stSidebar"] [data-testid="stBaseButton-primary"],
[data-testid="stSidebar"] button[kind="primary"] {
  background: var(--blue-light) !important;
  border-left: 3px solid var(--blue) !important;
  color: var(--blue) !important;
  font-weight: 700 !important;
}
[data-testid="stSidebar"] button[data-testid="baseButton-primary"]:hover {
  background: var(--blue-sky) !important;
  color: var(--blue) !important;
}

/* ── 공통 버튼 ── */
.stButton > button {
  border-radius: 7px;
  font-family: 'Noto Sans KR', sans-serif;
  font-weight: 600;
}

/* ── 사이드바 로고 ── */
.sidebar-logo {
  font-size: 18px;
  font-weight: 900;
  letter-spacing: 3px;
  color: var(--ink);
  padding: 4px 0 14px;
  text-align: center;
  border-bottom: 1px solid var(--border);
  margin-bottom: 6px;
}
</style>
""", unsafe_allow_html=True)

# ── 상태 초기화 ──────────────────────────────────────────────
init_state()

# ── 로그인 체크 ──────────────────────────────────────────────
if not st.session_state.get("logged_in"):
    login_screen()
    st.stop()

# ── 사이드바 ─────────────────────────────────────────────────
with st.sidebar:
    cfg  = st.session_state.cfg
    user = st.session_state.user

    # 로고
    st.markdown('<div class="sidebar-logo">LOTTE TASK</div>', unsafe_allow_html=True)

    unit_name  = cfg["units"].get(user["cell"], {}).get("name",  user["cell"])
    unit_color = cfg["units"].get(user["cell"], {}).get("color", "#1d4ed8")

    # 유저 정보 카드
    st.markdown(f"""
    <div style="background:#f8fafc;border-radius:8px;padding:8px 12px;
                margin-bottom:8px;font-size:13px;border:1px solid #e5e7eb;
                display:flex;align-items:center;gap:8px">
      <span style="background:{unit_color};padding:2px 8px;border-radius:4px;
                   font-size:11px;font-weight:700;color:white;flex-shrink:0">{unit_name}</span>
      <span style="color:#374151;font-weight:500">{user['name']}</span>
    </div>
    """, unsafe_allow_html=True)

    # 네비게이션
    pages = {
        "📊 대시보드":    "dashboard",
        "✅ Task Board":  "tasks",
        "📅 캘린더":      "calendar",
        "📁 파일 저장소": "files",
        "📝 메모장":      "memo",
    }
    if user["cell"] == "manager":
        pages["🌐 전체 공유 피드"] = "shared_feed"
        pages["⚙️ 어드민 설정"]   = "admin"

    if "current_page" not in st.session_state:
        st.session_state.current_page = "dashboard"

    for label, key in pages.items():
        is_active = st.session_state.current_page == key
        if st.button(label, key=f"nav_{key}",
                     use_container_width=True,
                     type="primary" if is_active else "secondary"):
            st.session_state.current_page = key
            st.rerun()

    st.divider()

    tasks_all = st.session_state.get("tasks", [])
    memos_all = st.session_state.get("memos", [])
    shared_count = (sum(1 for t in tasks_all if t.get("shared")) +
                    sum(1 for m in memos_all if m.get("shared")))
    st.caption(f"🟢 공유 항목 {shared_count}개")

    if st.button("🚪 로그아웃", use_container_width=True):
        st.session_state.logged_in = False
        st.session_state.user = None
        st.rerun()

# ── 페이지 라우팅 ────────────────────────────────────────────
page = st.session_state.get("current_page", "dashboard")

if page == "dashboard":
    dashboard.render()
elif page == "tasks":
    taskboard.render()
elif page == "calendar":
    calendar_view.render()
elif page == "files":
    files_view.render()
elif page == "memo":
    memo_view.render()
elif page == "shared_feed":
    shared_feed.render()
elif page == "admin":
    if st.session_state.user.get("cell") == "manager":
        admin_view.render()
    else:
        st.error("팀장 권한이 필요합니다.")
