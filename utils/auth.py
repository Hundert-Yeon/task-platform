"""
utils/auth.py
로그인 화면 렌더링
"""
import streamlit as st
from utils.state import _load_team, sync_tasks_to_calendar


def login_screen():
    branch_cfg = st.session_state.get("branch_cfg", {})
    branch     = branch_cfg.get("branch_name", "인천점")

    st.markdown("""
    <style>
    /* 점장 토글 버튼 - 링크처럼 보이게 */
    div[data-testid="stButton"].sm-toggle > button {
        background: transparent !important;
        border: none !important;
        box-shadow: none !important;
        color: #9ca3af !important;
        font-size: 11px !important;
        font-weight: 300 !important;
        padding: 0 4px !important;
        text-decoration: underline;
        white-space: nowrap !important;
    }
    div[data-testid="stButton"].sm-toggle > button:hover {
        color: #6b7280 !important;
        background: transparent !important;
    }
    </style>
    """, unsafe_allow_html=True)

    _, col_c, _ = st.columns([1, 2, 1])

    with col_c:
        # ── 브랜딩 ──────────────────────────────────────────────
        st.markdown(f"""
        <div style="text-align:center;padding:20px 0 10px">
            <div style="font-size:28px;font-weight:900;letter-spacing:4px;color:#c9b99a">LOTTE</div>
            <div style="font-size:13px;color:#8a7d6e;letter-spacing:3px">DEPARTMENT STORE</div>
            <div style="font-size:22px;font-weight:700;color:#1a3461;letter-spacing:2px;margin-top:8px">{branch}</div>
        </div>
        """, unsafe_allow_html=True)

        st.divider()

        show_sm = st.session_state.get("show_sm_login", False)

        if not show_sm:
            # ── 일반 로그인 ─────────────────────────────────────
            _render_member_login(branch_cfg)

            # 안내문
            st.markdown("""
            <div style="text-align:center;margin-top:14px;font-size:11px;color:#9ca3af;line-height:1.7">
                본인 소속 업무만 기본 열람됩니다. 전체 공유 설정 시 팀 전체에 공개됩니다.
            </div>
            """, unsafe_allow_html=True)

            # 점장 토글 버튼
            _, btn_col, _ = st.columns([1, 1, 1])
            with btn_col:
                st.markdown('<div class="sm-toggle">', unsafe_allow_html=True)
                if st.button("점장/부문장 로그인", use_container_width=True,
                             key="sm_login_toggle"):
                    st.session_state.show_sm_login = True
                    st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)

        else:
            # ── 점장/부문장 로그인 ──────────────────────────────
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
        placeholder="-- 팀을 선택하세요 --",
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
        placeholder="-- 선택하세요 --",
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
                    background:#f8fafc;border-radius:7px;border:1px solid #e5e7eb;
                    margin-top:-6px;margin-bottom:4px">
          <span style="font-size:13px;font-weight:600;color:#111827">{name_input.strip()}</span>
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
    <div style="text-align:center;margin-bottom:16px">
        <div style="font-size:13px;font-weight:600;color:#374151;letter-spacing:0.5px">
            점장 / 부문장 로그인
        </div>
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

    st.markdown("<div style='margin-top:8px'></div>", unsafe_allow_html=True)
    if st.button("← 일반 로그인으로 돌아가기", use_container_width=True, key="sm_back_btn"):
        st.session_state.show_sm_login = False
        st.rerun()
