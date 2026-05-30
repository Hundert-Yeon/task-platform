"""
utils/auth.py
로그인 화면 렌더링
"""
import streamlit as st
from utils.state import _load_team, sync_tasks_to_calendar

_DARK_CSS = """
<style>
/* ── 로그인 전용 다크 배경 ── */
.stApp,
[data-testid="stAppViewContainer"],
[data-testid="stHeader"],
.main .block-container {
    background: #09090f !important;
    background-color: #09090f !important;
    padding-top: 0 !important;
}
section[data-testid="stMain"] > div { background: #09090f !important; }

/* 입력 필드 */
[data-testid="stTextInput"] input {
    background: #13131f !important;
    color: #e5e7eb !important;
    border: 1px solid rgba(201,185,154,0.2) !important;
    border-radius: 8px !important;
}
[data-testid="stTextInput"] input::placeholder { color: #4b5563 !important; }
[data-testid="stTextInput"] input:focus {
    border-color: rgba(201,185,154,0.55) !important;
    box-shadow: 0 0 0 2px rgba(201,185,154,0.1) !important;
}

/* 셀렉트박스 */
[data-testid="stSelectbox"] > div > div {
    background: #13131f !important;
    color: #e5e7eb !important;
    border: 1px solid rgba(201,185,154,0.2) !important;
    border-radius: 8px !important;
}
[data-testid="stSelectbox"] svg { color: #9ca3af !important; fill: #9ca3af !important; }

/* 레이블 */
[data-testid="stTextInput"] label p,
[data-testid="stSelectbox"] label p {
    color: #6b7280 !important;
    font-size: 11px !important;
    letter-spacing: 0.5px !important;
}

/* 구분선 */
hr { border-color: rgba(255,255,255,0.07) !important; }

/* Primary 버튼 (입장하기) */
button[data-testid="baseButton-primary"],
[data-testid="stBaseButton-primary"] {
    background: rgba(201,185,154,0.15) !important;
    border: 1px solid rgba(201,185,154,0.4) !important;
    color: #c9b99a !important;
    letter-spacing: 1px !important;
    font-weight: 600 !important;
}
button[data-testid="baseButton-primary"]:hover,
[data-testid="stBaseButton-primary"]:hover {
    background: rgba(201,185,154,0.25) !important;
    border-color: rgba(201,185,154,0.7) !important;
    color: #e5d9c3 !important;
}

/* 에러 */
[data-testid="stAlert"][data-baseweb="notification"] {
    background: rgba(220,38,38,0.12) !important;
    border-color: rgba(220,38,38,0.3) !important;
    color: #fca5a5 !important;
}

/* 링크 버튼 (점장/일반 전환) */
.st-key-goto_sm_login button,
.st-key-goto_member_login button {
    background: none !important;
    border: none !important;
    box-shadow: none !important;
    color: #374151 !important;
    font-size: 11px !important;
    font-weight: 300 !important;
    letter-spacing: 0.3px !important;
    padding: 2px 0 !important;
    min-height: 0 !important;
    height: auto !important;
    width: auto !important;
}
.st-key-goto_sm_login button:hover,
.st-key-goto_member_login button:hover { color: #6b7280 !important; }
.st-key-goto_sm_login { text-align: center !important; }
</style>
"""


def login_screen():
    st.markdown(_DARK_CSS, unsafe_allow_html=True)

    branch_cfg = st.session_state.get("branch_cfg", {})
    branch     = branch_cfg.get("branch_name", "인천점")

    # 전체 화면 세로 중앙 정렬 패딩
    st.markdown("<div style='padding-top:8vh'></div>", unsafe_allow_html=True)

    _, col_c, _ = st.columns([1, 1.4, 1])

    with col_c:
        # ── 브랜딩 ──────────────────────────────────────────────
        st.markdown(f"""
        <div style="text-align:center;padding:0 0 28px">
            <div style="font-size:11px;color:#3d3d4a;letter-spacing:6px;
                        font-weight:400;margin-bottom:14px">— WELCOME —</div>
            <div style="font-size:30px;font-weight:900;letter-spacing:6px;
                        color:#c9b99a;text-shadow:0 0 40px rgba(201,185,154,0.25)">LOTTE</div>
            <div style="font-size:11px;color:#4a4a5a;letter-spacing:4px;
                        font-weight:300;margin-top:4px">DEPARTMENT STORE</div>
            <div style="font-size:18px;font-weight:600;color:#9ca3af;
                        letter-spacing:3px;margin-top:14px">{branch}</div>
        </div>
        """, unsafe_allow_html=True)

        # 얇은 골드 구분선
        st.markdown("""
        <div style="height:1px;background:linear-gradient(90deg,transparent,rgba(201,185,154,0.35),transparent);
                    margin-bottom:28px"></div>
        """, unsafe_allow_html=True)

        show_sm = st.session_state.get("show_sm_login", False)

        if not show_sm:
            _render_member_login(branch_cfg)

            st.markdown("""
            <div style="text-align:center;margin-top:14px">
                <div style="font-size:11px;color:#2d2d3a;line-height:2">
                    본인 소속 업무만 기본 열람됩니다.
                </div>
            </div>
            """, unsafe_allow_html=True)

            if st.button("점장 / 부문장 로그인", key="goto_sm_login"):
                st.session_state.show_sm_login = True
                st.rerun()
        else:
            _render_store_manager_login(branch_cfg)


def _render_member_login(branch_cfg: dict):
    """일반 팀원 / 팀장 로그인"""
    teams_data = st.session_state.get("teams_data", {})

    team_options = {tid: td["cfg"]["team_name"] for tid, td in teams_data.items()}
    if not team_options:
        st.error("등록된 팀이 없습니다.")
        return

    selected_team_id = st.selectbox(
        "소속 팀",
        options=list(team_options.keys()),
        format_func=lambda x: team_options[x],
        index=None,
        placeholder="팀을 선택하세요",
        key="login_team_sel",
    )

    if not selected_team_id:
        return

    team_cfg = teams_data[selected_team_id]["cfg"]
    units    = team_cfg.get("units", {})

    unit_options = {uid: f"{u['emoji']} {u['name']} · {u['type']}" for uid, u in units.items()}
    unit_options["manager"] = f"👑 {team_cfg['team_name']} 팀장"

    selected_cell = st.selectbox(
        "소속 / 역할",
        options=list(unit_options.keys()),
        format_func=lambda x: unit_options[x],
        index=None,
        placeholder="소속을 선택하세요",
        key="login_cell_sel",
    )

    name_input = st.text_input("이름", placeholder="이름을 입력하세요", key="login_name")

    if selected_cell and name_input.strip():
        if selected_cell == "manager":
            badge_color = "#1d4ed8"
            badge_text  = f"{team_cfg['team_name']} 팀장"
        else:
            u_info      = units.get(selected_cell, {})
            badge_color = u_info.get("color", "#6b7280")
            badge_text  = u_info.get("name", "")
        st.markdown(f"""
        <div style="display:flex;align-items:center;gap:8px;padding:7px 12px;
                    background:rgba(255,255,255,0.04);border-radius:8px;
                    border:1px solid rgba(201,185,154,0.15);margin-top:-6px;margin-bottom:4px">
          <span style="font-size:13px;font-weight:600;color:#d1d5db">{name_input.strip()}</span>
          <span style="background:{badge_color};color:white;font-size:10px;
                       font-weight:700;padding:2px 9px;border-radius:4px">{badge_text}</span>
        </div>
        """, unsafe_allow_html=True)

    pw_input = None
    if selected_cell == "manager":
        pw_input = st.text_input("팀장 비밀번호", type="password", placeholder="비밀번호 입력",
                                 key="login_mgr_pw")

    if st.button("입장하기 →", use_container_width=True, type="primary", key="login_member_btn"):
        if not selected_cell:
            st.error("소속/역할을 선택해주세요")
            return
        if not name_input.strip():
            st.error("이름을 입력해주세요")
            return
        if selected_cell == "manager":
            if pw_input != team_cfg.get("manager_pw", "0000"):
                st.error("비밀번호가 올바르지 않습니다")
                return

        _load_team(selected_team_id)
        sync_tasks_to_calendar()

        st.session_state.logged_in    = True
        st.session_state.current_page = "dashboard"
        st.session_state.user = {
            "cell":    selected_cell,
            "name":    name_input.strip(),
            "team_id": selected_team_id,
            "role":    "manager" if selected_cell == "manager" else "member",
        }
        st.rerun()


def _render_store_manager_login(branch_cfg: dict):
    """점장/부문장 로그인 화면"""
    st.markdown("""
    <div style="font-size:11px;color:#4a4a5a;letter-spacing:2px;
                font-weight:300;margin-bottom:16px;text-align:center">
        점장 / 부문장
    </div>
    """, unsafe_allow_html=True)

    name_input = st.text_input("이름", placeholder="이름을 입력하세요", key="login_sm_name")
    pw_input   = st.text_input("비밀번호", type="password", placeholder="비밀번호를 입력하세요",
                               key="login_sm_pw")

    if st.button("입장하기 →", use_container_width=True, type="primary", key="login_sm_btn"):
        if not name_input.strip():
            st.error("이름을 입력해주세요")
            return
        store_pw = branch_cfg.get("store_manager_pw", "0000")
        if pw_input != store_pw:
            st.error("비밀번호가 올바르지 않습니다")
            return

        st.session_state.logged_in    = True
        st.session_state.current_page = "dashboard"
        st.session_state.pop("sm_team_confirmed", None)
        st.session_state.show_sm_login = False
        st.session_state.user = {
            "cell":    "store_manager",
            "name":    name_input.strip(),
            "team_id": None,
            "role":    "store_manager",
        }
        st.rerun()

    if st.button("← 일반 로그인", key="goto_member_login"):
        st.session_state.show_sm_login = False
        st.rerun()
