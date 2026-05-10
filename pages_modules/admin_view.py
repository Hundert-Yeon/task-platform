"""
pages_modules/admin_view.py  — 어드민 설정 (팀장 전용)
"""
import streamlit as st
import pathlib
from utils.state import TYPE_OPTIONS, DEFAULT_MENU_VISIBILITY, _build_team_cfg, _load_team


def render():
    if st.session_state.user.get("cell") != "manager":
        st.error("팀장 권한이 필요합니다.")
        return

    st.markdown("### ⚙️ 어드민 설정")
    st.caption("팀/유닛/셀/파트 관리 · 팀장 비밀번호 변경 · 시스템 설정")

    cfg = st.session_state.cfg

    # ── 통계 ──────────────────────────────────────────────────
    tasks  = st.session_state.get("tasks", [])
    memos  = st.session_state.get("memos", [])
    files  = st.session_state.get("files", [])
    units  = cfg.get("units", {})

    c1, c2, c3 = st.columns(3)
    c1.metric("전체 Task",          len(tasks))
    c2.metric("유닛/셀/파트 수",     len(units))
    c3.metric("메모·파일",          len(memos) + len(files))

    st.divider()

    # ── 메뉴 표시 설정 (전체 너비) ───────────────────────────────
    st.markdown("#### 🗂️ 메뉴 표시 설정")
    st.caption("일반 팀원에게 보여줄 메뉴를 선택하세요. 팀장은 항상 전체 메뉴를 볼 수 있습니다.")

    MENU_ITEMS = {
        "dashboard":   "📊 대시보드",
        "tasks":       "✅ Task Board",
        "calendar":    "📅 캘린더",
        "files":       "📁 파일 저장소",
        "memo":        "📝 메모장",
        "shared_feed": "🌐 전체 공유 피드",
    }
    vis = cfg.get("menu_visibility", {k: True for k in MENU_ITEMS})

    with st.form("menu_vis_form"):
        cols_m = st.columns(3)
        new_vis = {}
        for i, (key, label) in enumerate(MENU_ITEMS.items()):
            new_vis[key] = cols_m[i % 3].checkbox(label, value=vis.get(key, True), key=f"mvis_{key}")
        if st.form_submit_button("메뉴 설정 저장", type="primary", use_container_width=True):
            cfg["menu_visibility"] = new_vis
            st.session_state.cfg = cfg
            st.success("메뉴 표시 설정이 저장됐습니다!")
            st.rerun()

    st.divider()

    col_left, col_right = st.columns(2)

    # ── 좌: 유닛/셀/파트 관리 ────────────────────────────────
    with col_left:
        st.markdown("#### 🏢 유닛 / 셀 / 파트 관리")
        st.caption(f"현재 팀: {cfg.get('team_name','')}")

        for uid, u in list(units.items()):
            with st.expander(f"{u['emoji']} {u['name']} ({u['type']})", expanded=False):
                with st.form(f"unit_form_{uid}"):
                    new_emoji = st.text_input("이모지", value=u.get("emoji","📁"), max_chars=2)
                    new_name  = st.text_input("이름",   value=u["name"])
                    cur_type  = u["type"] if u["type"] in TYPE_OPTIONS else "유닛"
                    new_type  = st.selectbox("유형", TYPE_OPTIONS,
                                             index=TYPE_OPTIONS.index(cur_type))
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
                            st.error("최소 1개의 유닛/셀/파트가 필요합니다")

        st.markdown("**+ 새 유닛/셀/파트 추가**")
        with st.form("add_unit_form"):
            a_col1, a_col2 = st.columns([1, 3])
            new_emoji = a_col1.text_input("이모지", value="📁", max_chars=2)
            new_name  = a_col2.text_input("이름")
            b_col1, b_col2 = st.columns(2)
            new_type  = b_col1.selectbox("유형", TYPE_OPTIONS)
            new_color = b_col2.color_picker("색상", value="#3b82f6")

            if st.form_submit_button("추가", type="primary", use_container_width=True):
                if new_name.strip():
                    base_id = new_name.lower().replace(" ", "_")[:12] or "unit"
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

    # ── 우: 설정 패널 ─────────────────────────────────────────
    with col_right:
        # 점·팀 이름 설정
        st.markdown("#### 🏬 점·팀 이름 설정")
        branch_cfg = st.session_state.get("branch_cfg", {})
        with st.form("names_form"):
            branch = st.text_input("점 이름", value=branch_cfg.get("branch_name", "인천점"))
            team   = st.text_input("팀 이름", value=cfg.get("team_name", "영업기획팀"))
            if st.form_submit_button("저장", type="primary", use_container_width=True):
                new_branch = branch.strip() or "인천점"
                st.session_state.branch_cfg["branch_name"] = new_branch
                cfg["branch_name"] = new_branch
                cfg["team_name"]   = team.strip() or "영업기획팀"
                st.session_state.cfg = cfg
                st.success("저장됐습니다!")

        st.divider()

        # ── AI API 키 설정 (영업기획팀 전용 — 전체 팀 공용) ────
        if st.session_state.get("current_team_id") == "sales_planning":
            st.markdown("#### 🤖 AI API 키 설정")
            st.caption("여기서 설정한 키는 모든 팀에서 공용으로 사용됩니다.")
            _render_api_key_section()
            st.divider()

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

    # ── 팀 관리 (전체 너비) ──────────────────────────────────────
    st.divider()
    _render_team_management()


def _render_team_management():
    """팀 생성 / 삭제 관리"""
    st.markdown("#### 🏗️ 팀 관리")
    st.caption("팀을 추가하거나 삭제합니다. 삭제 시 해당 팀의 모든 데이터가 제거됩니다.")

    teams_data      = st.session_state.get("teams_data", {})
    current_team_id = st.session_state.get("current_team_id", "")
    branch_cfg      = st.session_state.get("branch_cfg", {})
    branch_name     = branch_cfg.get("branch_name", "인천점")

    t_col1, t_col2 = st.columns(2)

    with t_col1:
        st.markdown("**등록된 팀 목록**")
        for tid, td in list(teams_data.items()):
            tcfg   = td["cfg"]
            tname  = tcfg.get("team_name", tid)
            is_cur = tid == current_team_id
            badge  = " ← 현재" if is_cur else ""

            with st.expander(f"🏢 {tname}{badge}", expanded=False):
                n_tasks = len(td.get("tasks", []))
                n_units = len(tcfg.get("units", {}))
                st.markdown(f"Task: **{n_tasks}건** · 유닛/셀/파트: **{n_units}개**")

                if is_cur:
                    st.info("현재 열람 중인 팀은 삭제할 수 없습니다.")
                elif len(teams_data) <= 1:
                    st.info("최소 1개의 팀이 필요합니다.")
                else:
                    confirm_key = f"confirm_del_team_{tid}"
                    if st.button(f"🗑 {tname} 팀 삭제", key=f"del_team_{tid}",
                                 use_container_width=True):
                        if st.session_state.get(confirm_key):
                            del st.session_state.teams_data[tid]
                            st.session_state.pop(confirm_key, None)
                            st.success(f"'{tname}' 팀이 삭제됐습니다.")
                            st.rerun()
                        else:
                            st.session_state[confirm_key] = True
                            st.warning(f"한번 더 누르면 '{tname}'과 모든 데이터가 삭제됩니다!")

    with t_col2:
        st.markdown("**새 팀 추가**")
        with st.form("add_team_form"):
            new_team_name = st.text_input("팀 이름", placeholder="예: 운영팀")
            new_mgr_pw    = st.text_input("팀장 비밀번호", value="0000",
                                          help="이 팀 팀장의 로그인 비밀번호")
            if st.form_submit_button("팀 추가", type="primary", use_container_width=True):
                if not new_team_name.strip():
                    st.error("팀 이름을 입력해주세요")
                else:
                    base_id = new_team_name.lower().replace(" ", "_")[:16] or "team"
                    tid = base_id
                    n = 1
                    while tid in teams_data:
                        tid = f"{base_id}{n}"; n += 1
                    st.session_state.teams_data[tid] = {
                        "cfg": {
                            "manager_pw":      new_mgr_pw or "0000",
                            "team_name":       new_team_name.strip(),
                            "branch_name":     branch_name,
                            "units":           {},
                            "menu_visibility": dict(DEFAULT_MENU_VISIBILITY),
                        },
                        "tasks":  [],
                        "events": [],
                        "memos":  [],
                        "files":  [],
                    }
                    st.success(f"'{new_team_name}' 팀이 추가됐습니다!")
                    st.rerun()


def _render_api_key_section():
    """AI API 키 입력 및 저장 (세션 + secrets.toml 파일 동시 저장)"""
    from utils.ai_helper import _get_api_key

    current_key = _get_api_key()

    # 현재 상태 표시
    if current_key:
        masked = current_key[:8] + "•" * 20 + current_key[-4:]
        st.markdown(f"""
        <div style="background:#ecfdf5;border:1.5px solid #a7f3d0;border-radius:8px;
                    padding:9px 13px;font-size:12.5px;color:#065f46;margin-bottom:10px;
                    display:flex;align-items:center;gap:8px">
          <span style="font-size:15px">✅</span>
          <span>API 키 설정됨 &nbsp;<code style="font-size:11px;color:#059669">{masked}</code></span>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style="background:#fef2f2;border:1.5px solid #fca5a5;border-radius:8px;
                    padding:9px 13px;font-size:12.5px;color:#991b1b;margin-bottom:10px;
                    display:flex;align-items:center;gap:8px">
          <span style="font-size:15px">⚠️</span>
          <span>API 키 미설정 — AI 기능이 비활성화됩니다</span>
        </div>
        """, unsafe_allow_html=True)

    with st.form("api_key_form"):
        new_key = st.text_input(
            "OpenAI API Key",
            type="password",
            placeholder="sk-...",
            help="OpenAI Platform에서 발급받은 API 키를 입력하세요",
        )
        save_col, test_col, clear_col = st.columns(3)
        save_clicked  = save_col.form_submit_button("💾 저장",   type="primary", use_container_width=True)
        test_clicked  = test_col.form_submit_button("🔗 테스트", use_container_width=True)
        clear_clicked = clear_col.form_submit_button("🗑 초기화", use_container_width=True)

    if save_clicked:
        if not new_key.strip():
            st.error("API 키를 입력해주세요.")
        elif not new_key.strip().startswith("sk-"):
            st.error("올바른 OpenAI API 키 형식이 아닙니다 (sk- 로 시작해야 합니다).")
        else:
            key = new_key.strip()
            st.session_state.runtime_api_key = key
            _save_key_to_secrets(key)
            st.session_state.pop("ai_checklist_cache", None)
            st.success("API 키가 저장됐습니다! 전체 팀 AI 기능이 활성화됩니다.")
            st.rerun()

    if test_clicked:
        key_to_test = new_key.strip() if new_key.strip() else current_key
        if not key_to_test:
            st.error("테스트할 API 키가 없습니다.")
        else:
            with st.spinner("API 연결 테스트 중..."):
                result = _test_api_key(key_to_test)
            if result is True:
                st.success("✅ API 연결 성공!")
            else:
                st.error(f"❌ 연결 실패: {result}")

    if clear_clicked:
        st.session_state.pop("runtime_api_key", None)
        _save_key_to_secrets("")
        st.session_state.pop("ai_checklist_cache", None)
        st.info("API 키가 초기화됐습니다.")
        st.rerun()


def _save_key_to_secrets(api_key: str):
    """secrets.toml 에 OPENAI_API_KEY 를 저장 (앱 재시작 후에도 유지)"""
    secrets_dir  = pathlib.Path(__file__).parent.parent / ".streamlit"
    secrets_file = secrets_dir / "secrets.toml"

    try:
        secrets_dir.mkdir(exist_ok=True)
        lines = []
        if secrets_file.exists():
            lines = secrets_file.read_text(encoding="utf-8").splitlines()

        lines = [l for l in lines if not l.strip().startswith("OPENAI_API_KEY")
                                  and not l.strip().startswith("ANTHROPIC_API_KEY")]
        if api_key:
            lines.append(f'OPENAI_API_KEY = "{api_key}"')

        secrets_file.write_text("\n".join(lines) + "\n", encoding="utf-8")
    except Exception as e:
        st.warning(f"secrets.toml 저장 실패 (세션 내에서만 적용됩니다): {e}")


def _test_api_key(api_key: str):
    """API 키 유효성 테스트. 성공이면 True, 실패면 오류 메시지 문자열 반환."""
    import requests as req
    try:
        resp = req.post(
            "https://api.openai.com/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type":  "application/json",
            },
            json={
                "model":      "gpt-4o-mini",
                "messages":   [{"role": "user", "content": "hi"}],
                "max_tokens": 5,
            },
            timeout=15,
        )
        if resp.ok:
            return True

        try:
            err  = resp.json().get("error", {})
            msg  = err.get("message", "")
            code = err.get("code", "")
        except Exception:
            msg  = resp.text[:150]
            code = ""

        if resp.status_code == 401:
            return "API 키가 유효하지 않습니다. 키를 다시 확인해주세요."
        elif resp.status_code == 429:
            if "insufficient_quota" in code or "quota" in msg.lower() or "billing" in msg.lower():
                return "계정 크레딧 부족 — OpenAI 플랫폼에서 결제 정보를 확인해주세요. (키 자체는 유효합니다)"
            else:
                return "분당 요청 한도 초과 — 잠시 후 다시 테스트해주세요. (키 자체는 유효합니다)"
        elif resp.status_code == 403:
            return "API 접근 권한 없음 — 키의 프로젝트 권한을 확인해주세요."
        else:
            return f"API 오류 ({resp.status_code}): {msg[:100] or resp.reason}"

    except req.exceptions.Timeout:
        return "요청 시간 초과 (15초) — 네트워크 상태를 확인해주세요."
    except req.exceptions.ConnectionError:
        return "OpenAI 서버에 연결할 수 없습니다. 네트워크를 확인해주세요."
    except Exception as e:
        return str(e)[:120]
