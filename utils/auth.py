"""
utils/auth.py
로그인 화면 렌더링
"""
import streamlit as st
from utils.state import _load_team, sync_tasks_to_calendar


def login_screen():
    branch_cfg = st.session_state.get("branch_cfg", {})
    branch     = branch_cfg.get("branch_name", "인천점")

    # 점장 로그인 토글 (query param 방식)
    q_sm = st.query_params.get("sm_login", None)
    if q_sm:
        st.session_state.show_sm_login = True
        st.query_params.clear()
        st.stop()

    st.markdown("""
    <style>
    body { background: linear-gradient(135deg,#0c1a35,#1a3461,#0f172a) !important; }
    .login-hint { font-size:11px;color:rgba(255,255,255,0.22);margin-top:14px;line-height:1.7; }
    </style>
    <div style="background:linear-gradient(135deg,#0c1a35,#1a3461,#0f172a);position:fixed;inset:0;z-index:-1"></div>
    """, unsafe_allow_html=True)

    col_l, col_c, col_r = st.columns([1, 2, 1])

    # ── 좌상단: 점장/부문장 진입 링크 ───────────────────────────
    with col_l:
        st.markdown("<div style='padding-top:24px'></div>", unsafe_allow_html=True)
        if st.session_state.get("show_sm_login"):
            st.markdown("""
            <div style="padding:6px 10px;background:rgba(255,255,255,0.07);
                        border:1px solid rgba(255,255,255,0.15);border-radius:7px;
                        display:inline-block">
              <span style="font-size:11px;color:rgba(255,255,255,0.55);font-weight:600;
                           letter-spacing:0.5px">점장 / 부문장</span>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <a href="?sm_login=1" style="text-decoration:none">
              <div style="padding:6px 10px;background:rgba(255,255,255,0.05);
                          border:1px solid rgba(255,255,255,0.12);border-radius:7px;
                          display:inline-block;cursor:pointer">
                <span style="font-size:11px;color:rgba(255,255,255,0.45);font-weight:500;
                             letter-spacing:0.5px">점장 / 부문장</span>
              </div>
            </a>
            """, unsafe_allow_html=True)

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

        # ── 기본 로그인 ─────────────────────────────────────────
        _render_member_login(branch_cfg)

        st.markdown("""
        <div class="login-hint" style="text-align:center">
            본인 소속 업무만 기본 열람됩니다. 전체 공유 설정 시 팀 전체에 공개됩니다.
        </div>
        """, unsafe_allow_html=True)

        # ── 점장/부문장 로그인 폼 (클릭 후 표시) ────────────────
        if st.session_state.get("show_sm_login"):
            st.markdown("<div style='margin-top:20px'></div>", unsafe_allow_html=True)
            _render_store_manager_section(branch_cfg)


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

    # 뱃지 프리뷰
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


def _render_store_manager_section(branch_cfg: dict):
    """점장/부문장 로그인 영역 (하단, 눈에 안 띄게)"""
    st.markdown("""
    <div style="border-top:1px solid rgba(255,255,255,0.1);padding-top:14px;margin-bottom:8px">
      <span style="font-size:11px;color:rgba(255,255,255,0.35);letter-spacing:1px">점장 / 부문장</span>
    </div>
    """, unsafe_allow_html=True)

    name_input = st.text_input("이름", placeholder="이름", key="login_sm_name")
    pw_input   = st.text_input("비밀번호", type="password", placeholder="••••",
                               key="login_sm_pw")

    c1, c2 = st.columns([3, 1])
    with c1:
        if st.button("입장", use_container_width=True, type="primary", key="login_sm_btn"):
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
    with c2:
        if st.button("닫기", use_container_width=True, key="login_sm_close"):
            st.session_state.show_sm_login = False
            st.rerun()
