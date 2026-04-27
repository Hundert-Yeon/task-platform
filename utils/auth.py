"""
utils/auth.py
로그인 화면 렌더링
"""
import streamlit as st
from utils.state import DEFAULT_CFG


def login_screen():
    cfg = st.session_state.get("cfg", DEFAULT_CFG)

    st.markdown("""
    <style>
    .login-wrap {
        max-width: 420px; margin: 60px auto 0;
        background: rgba(255,255,255,0.06);
        border: 1px solid rgba(255,255,255,0.14);
        border-radius: 18px; padding: 40px 36px;
        backdrop-filter: blur(24px);
        box-shadow: 0 24px 80px rgba(0,0,0,0.45);
        text-align: center;
    }
    body { background: linear-gradient(135deg,#0c1a35,#1a3461,#0f172a) !important; }
    .login-branch  { font-size: 22px; font-weight: 700; color: #1a3461; letter-spacing:2px; margin-top:10px; }
    .login-team    { font-size: 13px; color: #6b7280; letter-spacing:1.5px; margin-top:3px; }
    .login-hint    { font-size: 11px; color: rgba(255,255,255,0.25); margin-top: 14px; line-height:1.7; }
    </style>
    <div style="background:linear-gradient(135deg,#0c1a35,#1a3461,#0f172a);position:fixed;inset:0;z-index:-1"></div>
    """, unsafe_allow_html=True)

    # 로고 + 점·팀 이름
    col_l, col_c, col_r = st.columns([1, 2, 1])
    with col_c:
        branch = cfg.get("branch_name", "인천점")
        team   = cfg.get("team_name", "영업기획팀")

        st.markdown(f"""
        <div style="text-align:center;padding:20px 0 10px">
            <div style="font-size:28px;font-weight:900;letter-spacing:4px;color:#c9b99a">LOTTE</div>
            <div style="font-size:13px;color:#8a7d6e;letter-spacing:3px">DEPARTMENT STORE</div>
            <div class="login-branch">{branch}</div>
            <div class="login-team">{team}</div>
        </div>
        """, unsafe_allow_html=True)

        st.divider()

        units = cfg.get("units", {})
        unit_options = {uid: f"{u['emoji']} {u['name']} · {u['type']}" for uid, u in units.items()}
        unit_options["manager"] = "👑 팀장 (전체 열람)"

        selected_cell = st.selectbox(
            "소속 팀 / 유닛 / 셀 선택",
            options=list(unit_options.keys()),
            format_func=lambda x: unit_options[x],
            index=None,
            placeholder="-- 선택하세요 --",
        )

        name_input = st.text_input("이름", placeholder="이름을 입력하세요")

        # 선택된 팀/유닛/셀 명칭을 이름 뒤에 뱃지로 표시
        if selected_cell and name_input.strip():
            if selected_cell == "manager":
                badge_color = "#1d4ed8"
                badge_text  = "팀장"
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
            pw_input = st.text_input("팀장 비밀번호", type="password", placeholder="비밀번호 입력")

        if st.button("입장하기 →", use_container_width=True, type="primary"):
            if not selected_cell:
                st.error("팀/유닛/셀을 선택해주세요")
                return
            if not name_input.strip():
                st.error("이름을 입력해주세요")
                return
            if selected_cell == "manager":
                if pw_input != cfg.get("manager_pw", "0000"):
                    st.error("비밀번호가 올바르지 않습니다")
                    return

            st.session_state.logged_in    = True
            st.session_state.current_page = "dashboard"
            st.session_state.user = {
                "cell": selected_cell,
                "name": name_input.strip(),
            }
            # 캘린더 동기화
            from utils.state import sync_tasks_to_calendar
            sync_tasks_to_calendar()
            st.rerun()

        st.markdown("""
        <div class="login-hint">
            각 유닛/셀 멤버는 본인 소속 업무만 기본 열람됩니다.<br>
            전체 공유 체크 시 전 팀원에게 공개됩니다.
        </div>
        """, unsafe_allow_html=True)
