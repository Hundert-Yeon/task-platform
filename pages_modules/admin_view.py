"""
pages_modules/admin_view.py  — 어드민 설정 (팀장 전용)
"""
import streamlit as st
import json


def render():
    if st.session_state.user.get("cell") != "manager":
        st.error("팀장 권한이 필요합니다.")
        return

    st.markdown("### ⚙️ 어드민 설정")
    st.caption("유닛/셀 관리 · 팀장 비밀번호 변경 · 시스템 설정")

    cfg = st.session_state.cfg

    # ── 통계 ──────────────────────────────────────────────────
    tasks  = st.session_state.get("tasks", [])
    memos  = st.session_state.get("memos", [])
    files  = st.session_state.get("files", [])
    units  = cfg.get("units", {})

    c1, c2, c3 = st.columns(3)
    c1.metric("전체 Task",    len(tasks))
    c2.metric("유닛/셀 수",   len(units))
    c3.metric("메모·파일",    len(memos) + len(files))

    st.divider()

    col_left, col_right = st.columns(2)

    # ── 좌: 유닛/셀 관리 ─────────────────────────────────────
    with col_left:
        st.markdown("#### 🏢 유닛 / 셀 관리")
        st.caption("이름·색상·이모지·유형 수정 가능")

        for uid, u in list(units.items()):
            with st.expander(f"{u['emoji']} {u['name']} ({u['type']})", expanded=False):
                with st.form(f"unit_form_{uid}"):
                    new_emoji = st.text_input("이모지", value=u.get("emoji","📁"), max_chars=2)
                    new_name  = st.text_input("이름",   value=u["name"])
                    new_type  = st.selectbox("유형", ["유닛","셀"],
                                             index=0 if u["type"]=="유닛" else 1)
                    new_color = st.color_picker("색상", value=u["color"])

                    s_col1, s_col2 = st.columns(2)
                    if s_col1.form_submit_button("저장", type="primary", use_container_width=True):
                        if new_name.strip():
                            cfg["units"][uid].update({
                                "emoji": new_emoji or "📁",
                                "name":  new_name.strip(),
                                "type":  new_type,
                                "color": new_color,
                            })
                            st.session_state.cfg = cfg
                            st.success(f"'{new_name}' 저장됐습니다!")
                            st.rerun()
                    if s_col2.form_submit_button("삭제", use_container_width=True):
                        if len(cfg["units"]) > 1:
                            confirm_key = f"confirm_del_{uid}"
                            if st.session_state.get(confirm_key):
                                st.session_state.tasks = [t for t in tasks if t["cell"] != uid]
                                del cfg["units"][uid]
                                st.session_state.cfg = cfg
                                st.success("삭제됐습니다")
                                st.rerun()
                            else:
                                st.session_state[confirm_key] = True
                                st.warning(f"한번 더 누르면 '{u['name']}'과 관련 Task가 삭제됩니다!")
                        else:
                            st.error("최소 1개의 유닛/셀이 필요합니다")

        # 새 유닛/셀 추가
        st.markdown("**+ 새 유닛/셀 추가**")
        with st.form("add_unit_form"):
            a_col1, a_col2 = st.columns([1, 3])
            new_emoji = a_col1.text_input("이모지", value="📁", max_chars=2)
            new_name  = a_col2.text_input("이름")
            b_col1, b_col2, b_col3 = st.columns(3)
            new_type  = b_col1.selectbox("유형", ["유닛","셀"])
            new_color = b_col2.color_picker("색상", value="#3b82f6")

            if st.form_submit_button("추가", type="primary", use_container_width=True):
                if new_name.strip():
                    base_id = new_name.lower().replace(" ","_")[:12] or "unit"
                    uid = base_id
                    n = 1
                    while uid in cfg["units"] or uid == "manager":
                        uid = f"{base_id}{n}"; n += 1
                    cfg["units"][uid] = {
                        "name":  new_name.strip(),
                        "emoji": new_emoji or "📁",
                        "type":  new_type,
                        "color": new_color,
                    }
                    st.session_state.cfg = cfg
                    st.success(f"'{new_name}' 추가됐습니다!")
                    st.rerun()

    # ── 우: 비밀번호 + 점·팀 이름 + 시스템 ───────────────────
    with col_right:
        # 점·팀 이름 설정
        st.markdown("#### 🏬 점·팀 이름 설정")
        with st.form("names_form"):
            branch = st.text_input("점 이름", value=cfg.get("branch_name","인천점"))
            team   = st.text_input("팀 이름", value=cfg.get("team_name","영업기획팀"))
            if st.form_submit_button("저장", type="primary", use_container_width=True):
                cfg["branch_name"] = branch.strip() or "인천점"
                cfg["team_name"]   = team.strip()   or "영업기획팀"
                st.session_state.cfg = cfg
                st.success("저장됐습니다!")

        st.divider()

        # 팀장 비밀번호 변경
        st.markdown("#### 🔑 팀장 비밀번호 변경")
        with st.form("pw_form"):
            cur_pw  = st.text_input("현재 비밀번호", type="password")
            new_pw  = st.text_input("새 비밀번호",  type="password")
            conf_pw = st.text_input("비밀번호 확인", type="password")
            if st.form_submit_button("변경", type="primary", use_container_width=True):
                if cur_pw != cfg.get("manager_pw","0000"):
                    st.error("현재 비밀번호가 올바르지 않습니다")
                elif len(new_pw) < 4:
                    st.error("새 비밀번호는 4자리 이상이어야 합니다")
                elif new_pw != conf_pw:
                    st.error("새 비밀번호가 일치하지 않습니다")
                else:
                    cfg["manager_pw"] = new_pw
                    st.session_state.cfg = cfg
                    st.success("비밀번호가 변경됐습니다!")

        st.divider()

        # 시스템 정보
        st.markdown("#### 📋 시스템 정보")
        shared_cnt = sum(1 for t in tasks if t.get("shared")) + sum(1 for m in memos if m.get("shared"))
        st.table({
            "항목": ["버전", "공유 항목", "등록 일정", "팀장 PW 길이"],
            "값":   ["v1.0 (Streamlit)", f"{shared_cnt}개",
                     str(len(st.session_state.get("events",[]))), f"{'●'*len(cfg.get('manager_pw','0000'))}"],
        })

        st.divider()

        # 위험 구역
        st.markdown("#### ⚠️ 데이터 관리")
        with st.expander("🔴 위험 구역 (되돌릴 수 없음)", expanded=False):
            if st.button("🗑️ 전체 Task 초기화", use_container_width=True, type="secondary"):
                if st.session_state.get("confirm_task_reset"):
                    st.session_state.tasks = []
                    st.session_state.events = [e for e in st.session_state.events if e.get("source") != "task"]
                    st.session_state.confirm_task_reset = False
                    st.success("전체 Task가 초기화됐습니다")
                    st.rerun()
                else:
                    st.session_state.confirm_task_reset = True
                    st.warning("한번 더 누르면 모든 Task가 삭제됩니다!")

            if st.button("💥 전체 데이터 초기화", use_container_width=True, type="secondary"):
                if st.session_state.get("confirm_full_reset"):
                    st.session_state.tasks  = []
                    st.session_state.events = []
                    st.session_state.memos  = []
                    st.session_state.files  = []
                    st.session_state.confirm_full_reset = False
                    st.success("전체 데이터가 초기화됐습니다")
                    st.rerun()
                else:
                    st.session_state.confirm_full_reset = True
                    st.warning("한번 더 누르면 Task·메모·파일·일정이 모두 삭제됩니다!")
