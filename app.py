import streamlit as st
import streamlit.components.v1 as _components
from pages_modules import dashboard, taskboard, calendar_view, files_view, memo_view, admin_view, shared_feed, board_view
from utils.state import init_state, switch_team, get_all_teams
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

/* ── Secondary 버튼: 컴팩트 (칸반 카드 액션 버튼 등) ── */
button[data-testid="baseButton-secondary"],
[data-testid="stBaseButton-secondary"] {
  font-size: 12px !important;
  padding: 4px 6px !important;
  white-space: nowrap !important;
  line-height: 1.3 !important;
}

/* ── Primary 버튼: 진파란색 (로그인·업무추가 등) ── */
button[data-testid="baseButton-primary"],
[data-testid="stBaseButton-primary"],
button[data-testid="baseButton-primaryFormSubmit"],
[data-testid="stBaseButton-primaryFormSubmit"] {
  background: #1d4ed8 !important;
  border: 1px solid #1e40af !important;
  color: white !important;
}
button[data-testid="baseButton-primary"]:hover,
[data-testid="stBaseButton-primary"]:hover,
button[data-testid="baseButton-primaryFormSubmit"]:hover,
[data-testid="stBaseButton-primaryFormSubmit"]:hover {
  background: #1e40af !important;
  border-color: #1e3a8a !important;
  color: white !important;
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

/* ════════════════════════════════════════════════════════
   모바일 반응형
   ════════════════════════════════════════════════════════ */

/* ── 태블릿 (≤ 900px) ─────────────────────────────────── */
@media (max-width: 900px) {
  .main .block-container {
    padding-left: 1rem !important;
    padding-right: 1rem !important;
  }
}

/* ── 모바일 (≤ 640px) ─────────────────────────────────── */
@media (max-width: 640px) {
  /* 여백 최소화 */
  .main .block-container {
    padding-left: 0.65rem !important;
    padding-right: 0.65rem !important;
    padding-top: 0.5rem !important;
    max-width: 100vw !important;
  }

  /* 모든 가로 컬럼 → 세로 스택 */
  div[data-testid="stHorizontalBlock"] {
    flex-wrap: wrap !important;
    gap: 0.4rem !important;
  }
  div[data-testid="stHorizontalBlock"] > div[data-testid="column"] {
    min-width: 100% !important;
    flex: 0 0 100% !important;
    width: 100% !important;
  }

  /* 터치 타겟: 최소 44px */
  .stButton > button,
  button[data-testid*="Button"] {
    min-height: 44px !important;
  }
  /* 사이드바 버튼도 동일 */
  [data-testid="stSidebar"] button {
    min-height: 44px !important;
    padding: 10px 9px !important;
  }

  /* iOS 자동 줌 방지: 입력 필드 font-size >= 16px */
  [data-testid="stTextInput"] input,
  [data-testid="stTextArea"] textarea,
  [data-testid="stSelectbox"] > div > div,
  [data-testid="stDateInput"] input,
  [data-testid="stNumberInput"] input {
    font-size: 16px !important;
  }

  /* 헤더 폰트 축소 */
  h3 { font-size: 1.05rem !important; line-height: 1.4 !important; }
  h2 { font-size: 1.15rem !important; }

  /* HTML 테이블(캘린더): 가로 스크롤 */
  .stMarkdown table {
    display: block !important;
    overflow-x: auto !important;
    -webkit-overflow-scrolling: touch !important;
    white-space: nowrap !important;
  }
  .stMarkdown table td,
  .stMarkdown table th {
    min-width: 40px !important;
    font-size: 11px !important;
    padding: 3px 4px !important;
  }

  /* Dialog(팝업) 모달: 화면 90% 폭 */
  [data-testid="stModal"] > div > div {
    width: 94vw !important;
    max-width: 94vw !important;
    margin: 0 auto !important;
  }

  /* Expander 내부 패딩 축소 */
  [data-testid="stExpander"] > div:last-child {
    padding: 0.5rem !important;
  }

  /* 사이드바 로고 폰트 축소 */
  .sidebar-logo {
    font-size: 15px !important;
    letter-spacing: 2px !important;
  }

  /* Secondary 버튼: 모바일에서 폰트 정상화 */
  button[data-testid="baseButton-secondary"],
  [data-testid="stBaseButton-secondary"] {
    font-size: 13px !important;
    padding: 6px 8px !important;
  }

  /* 캡션/메타 텍스트 */
  [data-testid="stCaptionContainer"] p {
    font-size: 11px !important;
  }

  /* Streamlit 상단 헤더 높이 최소화 */
  [data-testid="stHeader"] {
    min-height: 2.75rem !important;
  }

  /* ── 사이드바 토글 버튼 복원 ──
     전역 CSS에서 stToolbar를 display:none 처리했는데
     모바일에서는 이 안에 사이드바 열기(☰) 버튼이 있으므로 다시 표시. */
  [data-testid="stToolbar"] {
    display: flex !important;
    background: var(--surface) !important;
    border-bottom: 1px solid var(--border) !important;
  }
  /* 사이드바 접힘 제어 버튼도 항상 노출 */
  [data-testid="collapsedControl"] {
    display: flex !important;
    visibility: visible !important;
    opacity: 1 !important;
  }
}

/* ── 극소형 모바일 (≤ 390px) ─────────────────────────── */
@media (max-width: 390px) {
  .main .block-container {
    padding-left: 0.4rem !important;
    padding-right: 0.4rem !important;
  }
  .sidebar-logo {
    font-size: 13px !important;
    letter-spacing: 1px !important;
  }
  h3 { font-size: 0.95rem !important; }
}
</style>
""", unsafe_allow_html=True)

# ── 상태 초기화 ──────────────────────────────────────────────
init_state()

# ── 로그인 체크 ──────────────────────────────────────────────
if not st.session_state.get("logged_in"):
    login_screen()
    st.stop()

user = st.session_state.user


def _render_sm_team_selection():
    branch_cfg = st.session_state.branch_cfg
    branch     = branch_cfg.get("branch_name", "인천점")
    all_teams  = get_all_teams()

    st.markdown(f"""
    <div style="background:linear-gradient(135deg,#0c1a35,#1a3461,#0f172a);
                position:fixed;inset:0;z-index:0"></div>
    <div style="position:relative;z-index:1;text-align:center;padding:52px 0 28px">
      <div style="font-size:22px;font-weight:900;letter-spacing:4px;color:#c9b99a">LOTTE</div>
      <div style="font-size:11px;color:#8a7d6e;letter-spacing:3px;margin-bottom:2px">DEPARTMENT STORE</div>
      <div style="font-size:18px;font-weight:700;color:white;letter-spacing:2px;margin-top:6px">{branch}</div>
      <div style="font-size:12px;color:rgba(255,255,255,0.5);margin-top:5px">
        {user['name']} 점장님, 열람할 팀을 선택하세요
      </div>
    </div>

    <style>
    /* 팀 선택 버튼 → 카드 스타일 */
    div[class*="st-key-sm_sel_"] button {{
        background: rgba(255,255,255,0.07) !important;
        border: 1px solid rgba(255,255,255,0.15) !important;
        border-radius: 12px !important;
        color: white !important;
        text-align: left !important;
        padding: 14px 20px !important;
        height: 60px !important;
        font-weight: 600 !important;
        font-size: 14px !important;
        letter-spacing: 0.2px !important;
        transition: all 0.18s ease !important;
    }}
    div[class*="st-key-sm_sel_"] button:hover {{
        background: rgba(255,255,255,0.14) !important;
        border-color: rgba(201,185,154,0.5) !important;
        color: #e8dcc8 !important;
        box-shadow: 0 4px 18px rgba(0,0,0,0.35) !important;
        transform: translateY(-1px) !important;
    }}
    div[class*="st-key-sm_sel_"] button p {{
        color: white !important;
        font-size: 14px !important;
    }}
    </style>
    """, unsafe_allow_html=True)

    teams_data = st.session_state.teams_data
    _, col_c, _ = st.columns([1, 2, 1])

    with col_c:
        for tid, tname in all_teams:
            td      = teams_data[tid]
            tcfg    = td["cfg"]
            n_tasks = len(td["tasks"])
            units   = tcfg.get("units", {})
            emojis  = "  ".join(u.get("emoji", "") for u in list(units.values()))
            label   = f"🏢  {tname}    {emojis}    ·  Task {n_tasks}건"
            if st.button(label, key=f"sm_sel_{tid}", use_container_width=True):
                switch_team(tid)
                st.session_state.sm_team_confirmed = True
                st.session_state.user["team_id"] = tid
                st.rerun()


# ── 점장: 팀 선택 화면 ──────────────────────────────────────
if user.get("cell") == "store_manager" and not st.session_state.get("sm_team_confirmed"):
    _render_sm_team_selection()
    st.stop()

# ── 사이드바 ─────────────────────────────────────────────────
with st.sidebar:
    cfg        = st.session_state.cfg
    branch_cfg = st.session_state.branch_cfg
    branch     = branch_cfg.get("branch_name", cfg.get("branch_name", "인천점"))
    team       = cfg.get("team_name", "영업기획팀")

    st.markdown(
        f"<div class='sidebar-logo'>{branch}"
        f"<br><span style='font-size:11px;font-weight:600;letter-spacing:1px;"
        f"color:#6b7280'>{team}</span></div>",
        unsafe_allow_html=True,
    )

    # 유저 배지
    if user["cell"] == "store_manager":
        unit_name  = "점장"
        unit_color = "#0f172a"
    elif user["cell"] == "manager":
        unit_name  = "팀장"
        unit_color = "#1d4ed8"
    else:
        unit_name  = cfg["units"].get(user["cell"], {}).get("name",  user["cell"])
        unit_color = cfg["units"].get(user["cell"], {}).get("color", "#1d4ed8")

    st.markdown(f"""
    <div style="background:#f8fafc;border-radius:8px;padding:8px 12px;
                margin-bottom:8px;font-size:13px;border:1px solid #e5e7eb;
                display:flex;align-items:center;gap:8px">
      <span style="background:{unit_color};padding:2px 8px;border-radius:4px;
                   font-size:11px;font-weight:700;color:white;flex-shrink:0">{unit_name}</span>
      <span style="color:#374151;font-weight:500">{user['name']}</span>
    </div>
    """, unsafe_allow_html=True)

    # 점장: 팀 전환 버튼
    if user["cell"] == "store_manager":
        all_teams       = get_all_teams()
        current_team_id = st.session_state.get("current_team_id", "")
        st.caption("🔀 팀 전환")
        t_cols = st.columns(len(all_teams))
        for i, (tid, tname) in enumerate(all_teams):
            is_cur = tid == current_team_id
            with t_cols[i]:
                if st.button(tname, key=f"sw_team_{tid}",
                             use_container_width=True,
                             type="primary" if is_cur else "secondary"):
                    switch_team(tid)
                    st.session_state.user["team_id"] = tid
                    st.session_state.current_page = "dashboard"
                    st.rerun()
        st.divider()

    # 네비게이션
    menu_vis = cfg.get("menu_visibility", {})
    ALL_PAGES = {
        "📊 대시보드":    "dashboard",
        "✅ Task Board":  "tasks",
        "📅 캘린더":      "calendar",
        "📁 파일 저장소": "files",
        "📝 메모장":      "memo",
        "📌 팀 익명게시판": "board",
    }

    global_files = st.session_state.branch_cfg.get("global_files_enabled", True)

    if user["cell"] in ("manager", "store_manager"):
        # 팀장/점장: menu_visibility 적용 + 전체공유피드 항상 표시
        pages = {
            label: key
            for label, key in ALL_PAGES.items()
            if (key != "files" or global_files) and (key != "board" or menu_vis.get("board", True))
        }
        if menu_vis.get("shared_feed", True):
            pages["🌐 전체 공유 피드"] = "shared_feed"
        # 팀 익명게시판: 팀장은 항상 볼 수 있음 (설정 페이지 접근용)
        if "📌 팀 익명게시판" not in pages:
            pages["📌 팀 익명게시판"] = "board"
        pages["💬 점 건의함(익명)"] = "branch_board"
        # 어드민은 팀장만 (점장 제외)
        if user["cell"] == "manager":
            pages["⚙️ 어드민 설정"] = "admin"
    else:
        pages = {
            label: key
            for label, key in ALL_PAGES.items()
            if menu_vis.get(key, True) and (key != "files" or global_files)
        }
        pages["💬 점 건의함(익명)"] = "branch_board"

    # 현재 페이지가 숨겨진 경우 첫 번째 표시 메뉴로 이동
    if st.session_state.get("current_page") not in pages.values():
        st.session_state.current_page = next(iter(pages.values()), "dashboard")

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
        st.session_state.user      = None
        st.session_state.pop("sm_team_confirmed", None)
        st.rerun()

# ── 페이지 라우팅 ────────────────────────────────────────────
page = st.session_state.get("current_page", "dashboard")

# 페이지가 바뀔 때만 스크롤 맨 위로 이동
if st.session_state.get("_last_page") != page:
    st.session_state["_last_page"] = page
    _components.html(
        """<script>
        var el = window.parent.document.querySelector('[data-testid="stAppViewContainer"]');
        if (el) el.scrollTop = 0;
        window.parent.scrollTo(0, 0);
        </script>""",
        height=0,
    )

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
elif page == "board":
    board_view.render()
elif page == "branch_board":
    board_view.render_branch_board()
elif page == "admin":
    if st.session_state.user.get("cell") == "manager":
        admin_view.render()
    else:
        st.error("팀장 권한이 필요합니다.")
