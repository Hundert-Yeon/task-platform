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
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;400;500;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Noto Sans KR', sans-serif;
}
.main .block-container { padding-top: 1.5rem; padding-bottom: 2rem; }
.stButton > button {
    border-radius: 7px;
    font-family: 'Noto Sans KR', sans-serif;
    font-weight: 600;
}
div[data-testid="stSidebarContent"] {
    background: #1a2e4a;
}
div[data-testid="stSidebarContent"] * { color: rgba(255,255,255,0.85) !important; }
.sidebar-logo {
    font-size: 22px; font-weight: 900; letter-spacing: 3px;
    color: #fff; padding: 8px 0 16px 0; text-align: center;
}
/* 칸반 컬럼 */
.kanban-header {
    padding: 8px 12px; border-radius: 6px 6px 0 0;
    font-weight: 700; font-size: 13px; color: white;
    margin-bottom: 0;
}
.task-card {
    background: white; border-radius: 8px; padding: 12px;
    margin: 6px 0; box-shadow: 0 1px 4px rgba(0,0,0,0.08);
    border-left: 3px solid #e5e7eb;
}
.task-card.shared { border-left-color: #059669; }
.task-card.high   { border-top: 2px solid #dc2626; }
.task-card.mid    { border-top: 2px solid #d97706; }
.task-card.low    { border-top: 2px solid #059669; }
/* AI 체크리스트 */
.ai-checklist-box {
    background: linear-gradient(135deg, #0f172a, #1e3a5f);
    border-radius: 10px; padding: 16px 18px; color: white;
}
.ai-item { 
    background: rgba(255,255,255,0.07); border-radius: 7px;
    padding: 8px 12px; margin: 5px 0; font-size: 13px;
}
/* 공유피드 */
.feed-item {
    display: flex; align-items: center; gap: 10px;
    padding: 8px 12px; border-bottom: 1px solid #e5e7eb;
    font-size: 12.5px;
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
    cfg = st.session_state.cfg
    st.markdown(f"""
    <div class="sidebar-logo">LOTTE TASK</div>
    """, unsafe_allow_html=True)

    user = st.session_state.user
    unit_name = cfg["units"].get(user["cell"], {}).get("name", user["cell"])
    unit_color = cfg["units"].get(user["cell"], {}).get("color", "#1d4ed8")

    st.markdown(f"""
    <div style="background:rgba(255,255,255,0.08);border-radius:8px;padding:8px 12px;margin-bottom:12px;font-size:13px">
        <span style="background:{unit_color};padding:2px 8px;border-radius:4px;font-size:11px;font-weight:700">{unit_name}</span>
        &nbsp; {user["name"]}
    </div>
    """, unsafe_allow_html=True)

    # 네비게이션
    pages = {
        "📊 대시보드":       "dashboard",
        "✅ Task Board":     "tasks",
        "📅 캘린더":         "calendar",
        "📁 파일 저장소":    "files",
        "📝 메모장":         "memo",
    }
    if user["cell"] == "manager":
        pages["🌐 전체 공유 피드"] = "shared_feed"
        pages["⚙️ 어드민 설정"]   = "admin"

    page_key = "current_page"
    if page_key not in st.session_state:
        st.session_state[page_key] = "dashboard"

    for label, key in pages.items():
        is_active = st.session_state[page_key] == key
        if st.button(label, key=f"nav_{key}",
                     use_container_width=True,
                     type="primary" if is_active else "secondary"):
            st.session_state[page_key] = key
            st.rerun()

    st.divider()
    # 공유 항목 수
    tasks = st.session_state.get("tasks", [])
    memos = st.session_state.get("memos", [])
    shared_count = sum(1 for t in tasks if t.get("shared")) + \
                   sum(1 for m in memos if m.get("shared"))
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
