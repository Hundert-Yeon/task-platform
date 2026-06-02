"""
pages_modules/taskboard.py
Task Board 페이지
"""
import streamlit as st
from datetime import date, timedelta
from utils.state import (
    get_visible_tasks, STATUS_LIST, new_id, today_str, sync_tasks_to_calendar
)

PRIORITY_LABELS = {"H": "높음", "M": "보통", "L": "낮음"}
PRIORITY_COLORS = {"H": "#dc2626", "M": "#d97706", "L": "#059669"}


def _esc(text: str) -> str:
    return str(text).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


@st.dialog("업무 상세", width="large")
def _task_detail_popup(task: dict):
    """업무 상세 정보 팝업"""
    cfg   = st.session_state.cfg
    units = cfg.get("units", {})
    status_map = {s["key"]: s for s in STATUS_LIST}

    unit_info  = units.get(task.get("cell", ""), {})
    unit_name  = unit_info.get("name", task.get("cell", ""))
    unit_color = unit_info.get("color", "#6b7280")

    pri        = task.get("pri", "M")
    pri_label  = PRIORITY_LABELS.get(pri, "보통")
    pri_color  = PRIORITY_COLORS.get(pri, "#d97706")

    status_info = status_map.get(task.get("status", "todo"), {})
    status_lbl  = status_info.get("label", "대기")
    status_col  = status_info.get("color", "#6b7280")

    shared_badge = (
        "<span style='font-size:12px;color:#7c3aed;font-weight:700'>🏢 부문·점 공유</span>"
        if task.get("shared_branch") else (
        "<span style='font-size:12px;color:#059669;font-weight:700'>🌐 팀 전체 공유</span>"
        if task.get("shared") else "")
    )

    st.markdown(f"""
    <div style='display:flex;flex-wrap:wrap;align-items:center;gap:8px;margin-bottom:14px'>
        <span style='background:{unit_color};color:white;font-size:12px;font-weight:700;
                     padding:3px 10px;border-radius:5px'>{_esc(unit_name)}</span>
        <span style='background:{pri_color}22;color:{pri_color};font-size:12px;font-weight:700;
                     padding:3px 10px;border-radius:5px'>{pri_label}</span>
        <span style='background:{status_col}22;color:{status_col};font-size:12px;font-weight:700;
                     padding:3px 10px;border-radius:5px'>{status_lbl}</span>
        {shared_badge}
    </div>
    <div style='font-size:18px;font-weight:700;color:#111827;margin-bottom:14px;
                border-left:4px solid {pri_color};padding-left:12px;line-height:1.4'>
        {_esc(task.get("title", ""))}
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    col1.info(f"👤 **담당자** : {_esc(task.get('assignee', '미정'))}")
    col2.info(f"📅 **마감일** : {task.get('due', '미정')}")

    if task.get("desc"):
        st.markdown("**📝 상세 내용**")
        st.markdown(
            f"<div style='background:#f8fafc;border-radius:7px;padding:10px 14px;"
            f"font-size:13px;color:#374151;border:1px solid #e5e7eb;white-space:pre-wrap'>"
            f"{_esc(task.get('desc',''))}</div>",
            unsafe_allow_html=True,
        )

    # ── AI 심층 분석 ──────────────────────────────────────
    from utils.ai_helper import get_ai_task_advice_detail, get_client as _gc
    _dk = f"task_advice_detail_{task['id']}"
    # API 키가 연결됐는데 "키 없음" 캐시가 남아 있으면 삭제 후 재생성
    _cached_det = st.session_state.get(_dk)
    if _gc() and isinstance(_cached_det, dict) and "GEMINI_API_KEY" in _cached_det.get("summary", ""):
        st.session_state.pop(_dk, None)
    if _dk not in st.session_state:
        if _gc():
            with st.spinner("AI 심층 분석 중..."):
                st.session_state[_dk] = get_ai_task_advice_detail(task)
        else:
            st.session_state[_dk] = get_ai_task_advice_detail(task)
    _det = st.session_state.get(_dk, {})
    if _det:
        _LVLC = {"urgent": "#fca5a5", "normal": "#93c5fd", "ok": "#6ee7b7"}
        _LVLL = {"urgent": "긴급", "normal": "확인", "ok": "양호"}
        _summary = _det.get("summary", "")
        _items   = _det.get("items", [])
        _rows = ""
        for _it in _items:
            _lv = _it.get("level", "normal")
            _rows += (
                f"<div style='background:rgba(255,255,255,0.07);border-radius:6px;"
                f"padding:7px 10px;margin:4px 0;display:flex;align-items:flex-start;"
                f"gap:8px;border:1px solid rgba(255,255,255,0.08)'>"
                f"<span style='font-size:13px;flex-shrink:0'>{_it.get('icon','📌')}</span>"
                f"<span style='font-size:12px;color:rgba(255,255,255,0.9);"
                f"flex:1;line-height:1.5'>{_esc(str(_it.get('text','')))}</span>"
                f"<span style='font-size:10px;font-weight:700;background:rgba(0,0,0,0.3);"
                f"color:{_LVLC.get(_lv,'#93c5fd')};padding:2px 6px;border-radius:4px;"
                f"flex-shrink:0'>{_LVLL.get(_lv,'확인')}</span>"
                f"</div>"
            )
        st.markdown(
            f"<div style='background:linear-gradient(135deg,#0f172a,#1e3a5f);"
            f"border-radius:10px;padding:14px 16px;margin-top:14px'>"
            f"<div style='font-size:11px;letter-spacing:2px;font-weight:700;"
            f"color:rgba(255,255,255,0.5);margin-bottom:8px'>✦ AI 심층 분석</div>"
            f"{'<div style=\"font-size:12.5px;color:rgba(255,255,255,0.85);line-height:1.6;margin-bottom:10px;background:rgba(255,255,255,0.05);border-radius:7px;padding:9px 12px\">' + _esc(_summary) + '</div>' if _summary else ''}"
            f"{_rows}"
            f"</div>",
            unsafe_allow_html=True,
        )

    st.divider()
    c1, c2 = st.columns(2)
    with c1:
        if st.button("✏️ 수정하기", type="primary", use_container_width=True):
            st.session_state.edit_task_id    = task["id"]
            st.session_state.show_task_modal = True
            st.rerun()
    with c2:
        if st.button("닫기", use_container_width=True):
            st.rerun()


def render():
    user  = st.session_state.user
    cfg   = st.session_state.cfg
    units = cfg.get("units", {})
    is_manager = user["cell"] in ("manager", "store_manager")

    if "detail_task_id" not in st.session_state:
        st.session_state.detail_task_id = None

    col_hdr, col_btn = st.columns([3, 1])
    with col_hdr:
        st.markdown("### ✅ Task Board")
        label = "전체 유닛/셀 업무" if is_manager else f"{units.get(user['cell'],{}).get('name','')} + 공유 업무"
        st.caption(label)
    with col_btn:
        if st.button("+ 업무 추가", type="primary", use_container_width=True):
            st.session_state.show_task_modal = True
            st.session_state.edit_task_id    = None

    # ── 필터 (팀장: 셀 필터) ──
    if is_manager:
        all_cells = {"all": "전체"} | {k: v["name"] for k, v in units.items()}
        filter_cell = st.selectbox(
            "셀 필터",
            options=list(all_cells.keys()),
            format_func=lambda x: all_cells[x],
            key="task_filter_cell",
        )
    else:
        filter_cell = "all"

    visible = get_visible_tasks()
    if filter_cell != "all":
        visible = [t for t in visible if t["cell"] == filter_cell]

    # ── AI 조언 사전 생성 (캐시 없는 Task + "키 없음" 구버전 캐시 재취득) ─────────
    from utils.ai_helper import get_ai_task_advice, get_client
    _api_on = get_client()

    def _advice_stale(_tid: str) -> bool:
        cached = st.session_state.get(f"task_advice_{_tid}")
        if not cached:
            return True
        # API 키가 연결됐는데 "키 없음" 메시지가 캐시되어 있으면 재취득
        if _api_on and isinstance(cached, list) and cached and cached[0].get("icon") == "🔑":
            return True
        return False

    _need = [t for t in visible if _advice_stale(t["id"])]
    if _need:
        _ctx = st.spinner(f"AI 조언 생성 중... ({len(_need)}건)") if _api_on else None
        if _ctx:
            with _ctx:
                for _t in _need:
                    st.session_state[f"task_advice_{_t['id']}"] = get_ai_task_advice(_t)
        else:
            for _t in _need:
                st.session_state[f"task_advice_{_t['id']}"] = get_ai_task_advice(_t)

    # ── 칸반 보드 ────────────────────────────────────────────
    today = date.today()
    in3   = today + timedelta(days=3)

    st.markdown("""<style>
div[data-testid="column"] > div[data-testid="stVerticalBlock"] { gap: 3px !important; }
div[data-testid="column"] > div[data-testid="stVerticalBlock"] > div[data-testid="element-container"] { margin-bottom: 0 !important; }
</style>""", unsafe_allow_html=True)

    cols  = st.columns(4, gap="small")

    for i, status in enumerate(STATUS_LIST):
        col_tasks = [t for t in visible if t["status"] == status["key"]]
        with cols[i]:
            st.markdown(
                f"<div style='background:{status['color']};color:white;padding:7px 11px;"
                f"border-radius:8px 8px 0 0;font-size:12px;font-weight:700;"
                f"margin-bottom:0'>"
                f"{status['label']} "
                f"<span style='opacity:.6;font-size:11px'>({len(col_tasks)})</span></div>",
                unsafe_allow_html=True,
            )

            for t in col_tasks:
                due_d   = date.fromisoformat(t["due"]) if t.get("due") else None
                is_ov   = due_d and due_d < today and t["status"] != "done"
                is_soon = due_d and today <= due_d <= in3 and t["status"] != "done"
                due_color  = "#dc2626" if is_ov else "#d97706" if is_soon else "#9ca3af"
                pri_color  = PRIORITY_COLORS.get(t.get("pri","M"), "#9ca3af")
                cell_color = units.get(t["cell"], {}).get("color", "#999")
                shared_ico = " 🏢" if t.get("shared_branch") else (" 🌐" if t.get("shared") else "")

                with st.container():
                    shared_bl = ("#7c3aed" if t.get("shared_branch")
                                 else ("#059669" if t.get("shared") else "#e5e7eb"))
                    cell_name = units.get(t["cell"], {}).get("name", t["cell"])
                    _uid      = t['id']
                    desc_str  = t.get("desc", "").strip()
                    _bk       = f"card{_uid}"
                    _pri_dot  = {"H": "🔴", "M": "🟡", "L": "🟢"}.get(t.get("pri", "M"), "🟡")
                    _pri_lbl  = PRIORITY_LABELS.get(t.get("pri", "M"), "보통")

                    # ── 카드 전체가 클릭 가능 + 액션버튼 컴팩트 CSS ──
                    st.markdown(
                        f"<style>"
                        f".st-key-{_bk} button{{"
                        f"background:white!important;"
                        f"border-top:2px solid {pri_color}!important;"
                        f"border-left:3px solid {shared_bl}!important;"
                        f"border-right:1px solid #e5e7eb!important;"
                        f"border-bottom:1px solid #e5e7eb!important;"
                        f"border-radius:8px 8px 4px 4px!important;"
                        f"text-align:left!important;padding:9px 12px 10px!important;"
                        f"width:100%!important;margin-top:6px!important;"
                        f"box-shadow:0 2px 5px rgba(0,0,0,0.06)!important;"
                        f"cursor:pointer!important;height:auto!important;"
                        f"white-space:pre-wrap!important;line-height:1.75!important;"
                        f"font-size:12.5px!important;font-weight:600!important;"
                        f"color:#111827!important;word-break:keep-all!important;"
                        f"transition:box-shadow 0.15s,transform 0.15s!important;}}"
                        f".st-key-{_bk} button:hover{{box-shadow:0 4px 14px rgba(0,0,0,0.13)!important;"
                        f"transform:translateY(-1px)!important;}}"
                        f".st-key-{_bk}{{margin-bottom:0px!important;}}"
                        f"div[data-testid='element-container']:has(>[data-testid='stHorizontalBlock'] .st-key-edit_{_uid})"
                        f"{{margin-top:0px!important;padding-top:0!important;}}"
                        f"div[data-testid='element-container']:has(.st-key-edit_{_uid}) [data-testid='stHorizontalBlock']"
                        f"{{gap:3px!important;}}"
                        f".st-key-edit_{_uid} button,.st-key-mv_{_uid} button,.st-key-del_{_uid} button{{"
                        f"font-size:11px!important;padding:0 4px!important;"
                        f"min-height:24px!important;height:24px!important;"
                        f"color:#9ca3af!important;border-color:#f0f0f0!important;"
                        f"background:#fafafa!important;border-radius:4px!important;"
                        f"font-weight:500!important;transition:all 0.1s!important;}}"
                        f".st-key-edit_{_uid} button:hover,.st-key-mv_{_uid} button:hover,.st-key-del_{_uid} button:hover{{"
                        f"color:#374151!important;border-color:#d1d5db!important;"
                        f"background:white!important;box-shadow:0 1px 3px rgba(0,0,0,0.08)!important;}}"
                        f"</style>",
                        unsafe_allow_html=True,
                    )

                    _sh_txt  = (" " + shared_ico.strip()) if shared_ico.strip() else ""
                    _btn_lbl = (
                        f"{_pri_dot} {_pri_lbl}  ·  {cell_name}{_sh_txt}\n"
                        f"{t['title']}\n"
                        f"마감 ~{t.get('due','')}  ·  👤 {t.get('assignee','미정')}"
                    )
                    if desc_str:
                        _prev = desc_str[:45] + ("..." if len(desc_str) > 45 else "")
                        _btn_lbl += f"\n{_prev}"

                    if st.button(_btn_lbl, key=_bk, use_container_width=True):
                        st.session_state.detail_task_id = _uid
                        st.rerun()

                    # ── 액션 버튼 3개 (컴팩트) ────────────────────
                    bc1, bc2, bc3 = st.columns(3, gap="small")
                    with bc1:
                        if st.button("✏️ 수정", key=f"edit_{_uid}", use_container_width=True):
                            st.session_state.edit_task_id    = _uid
                            st.session_state.show_task_modal = True
                    with bc2:
                        nst_label, nst_key = _next_status(t["status"])
                        btn_lbl = f"→{nst_label}" if nst_label else "─"
                        if st.button(btn_lbl, key=f"mv_{_uid}", use_container_width=True,
                                     disabled=not nst_key):
                            t["status"] = nst_key
                            sync_tasks_to_calendar()
                            st.rerun()
                    with bc3:
                        if st.button("🗑 삭제", key=f"del_{_uid}", use_container_width=True):
                            st.session_state.tasks = [x for x in st.session_state.tasks
                                                      if x["id"] != _uid]
                            sync_tasks_to_calendar()
                            st.rerun()

                    # ── AI 조언 (최대 2개, 자동 표시) ──────────
                    _adv_key   = f"task_advice_{_uid}"
                    _adv_items = st.session_state.get(_adv_key)
                    if _adv_items:
                        _LVLC = {"urgent":"#fca5a5","normal":"#93c5fd","ok":"#6ee7b7"}
                        _LVLL = {"urgent":"긴급","normal":"확인","ok":"양호"}
                        _rows = ""
                        _src  = _adv_items if isinstance(_adv_items, list) else []
                        for _it in _src[:2]:
                            _lv = _it.get("level","normal")
                            _rows += (
                                f"<div style='background:rgba(255,255,255,0.07);border-radius:6px;"
                                f"padding:6px 8px;margin:3px 0;display:flex;align-items:flex-start;"
                                f"gap:7px;border:1px solid rgba(255,255,255,0.08)'>"
                                f"<span style='font-size:12px;flex-shrink:0'>{_it.get('icon','📌')}</span>"
                                f"<span style='font-size:11px;color:rgba(255,255,255,0.9);"
                                f"flex:1;line-height:1.5'>{_esc(str(_it.get('text','')))}</span>"
                                f"<span style='font-size:9px;font-weight:700;background:rgba(0,0,0,0.3);"
                                f"color:{_LVLC.get(_lv,'#93c5fd')};padding:1px 5px;border-radius:3px;"
                                f"flex-shrink:0'>{_LVLL.get(_lv,'확인')}</span>"
                                f"</div>"
                            )
                        if _rows:
                            st.markdown(f"""
                            <div style="background:linear-gradient(135deg,#0f172a,#1e3a5f);
                                        border-radius:8px;padding:10px 12px;margin:3px 0 8px">
                              <div style="font-size:9px;letter-spacing:2px;font-weight:700;
                                          color:rgba(255,255,255,0.45);margin-bottom:6px">✦ AI 조언</div>
                              {_rows}
                            </div>
                            """, unsafe_allow_html=True)

            # 컬럼 하단 추가 버튼
            st.markdown(
                f"<style>.st-key-add_col_{status['key']} button{{"
                f"color:#9ca3af!important;border-color:#e5e7eb!important;"
                f"background:#fafafa!important;font-size:14px!important;"
                f"min-height:28px!important;height:28px!important;"
                f"border-style:dashed!important;border-radius:6px!important;"
                f"padding:0!important;transition:all 0.1s!important;}}"
                f".st-key-add_col_{status['key']} button:hover{{"
                f"color:#6b7280!important;border-color:#9ca3af!important;"
                f"background:white!important;}}</style>",
                unsafe_allow_html=True,
            )
            if st.button("＋", key=f"add_col_{status['key']}", use_container_width=True):
                st.session_state.show_task_modal = True
                st.session_state.edit_task_id    = None
                st.session_state.default_status  = status["key"]

    # ── 업무 상세 팝업 ───────────────────────────────────────
    if st.session_state.get("detail_task_id"):
        det_task = next(
            (t for t in st.session_state.tasks
             if t["id"] == st.session_state.detail_task_id),
            None,
        )
        if det_task:
            _task_detail_popup(det_task)
        st.session_state.detail_task_id = None

    # ── 업무 추가/수정 모달 ───────────────────────────────────
    if st.session_state.get("show_task_modal"):
        _task_form()
        st.session_state.show_task_modal = False


def _next_status(current: str) -> tuple[str, str] | tuple[None, None]:
    transitions = {
        "todo":  ("진행", "inprog"),
        "inprog": ("완료", "done"),
        "hold":  ("진행", "inprog"),
    }
    pair = transitions.get(current)
    return pair if pair else (None, None)


@st.dialog("업무 추가 / 수정", width="large")
def _task_form():
    """업무 추가/수정 팝업 다이얼로그"""
    edit_id  = st.session_state.get("edit_task_id")
    edit_task = next((t for t in st.session_state.tasks if t["id"] == edit_id), None) if edit_id else None

    user  = st.session_state.user
    cfg   = st.session_state.cfg
    units = cfg.get("units", {})
    is_manager = user["cell"] in ("manager", "store_manager")

    with st.form("task_modal_form"):
        title = st.text_input("업무명 *", value=edit_task["title"] if edit_task else "")

        col1, col2 = st.columns(2)
        with col1:
            pri_opts = ["H", "M", "L"]
            pri_idx  = pri_opts.index(edit_task["pri"]) if edit_task else 1
            pri = st.selectbox("우선순위", pri_opts,
                               format_func=lambda x: {"H":"높음","M":"보통","L":"낮음"}[x],
                               index=pri_idx)
        with col2:
            st_opts = [s["key"] for s in STATUS_LIST]
            st_labels = {s["key"]: s["label"] for s in STATUS_LIST}
            default_st = edit_task["status"] if edit_task else st.session_state.get("default_status","todo")
            st_idx = st_opts.index(default_st) if default_st in st_opts else 0
            status = st.selectbox("상태", st_opts, format_func=lambda x: st_labels[x], index=st_idx)

        col3, col4 = st.columns(2)
        with col3:
            assignee = st.text_input("담당자", value=edit_task.get("assignee", user["name"]) if edit_task else user["name"])
        with col4:
            due_val = date.fromisoformat(edit_task["due"]) if edit_task and edit_task.get("due") else date.today() + timedelta(days=7)
            due = st.date_input("마감일", value=due_val)

        desc = st.text_area("상세 내용", value=edit_task.get("desc","") if edit_task else "", height=70)
        _s_opts = ["비공개", "팀 전체 공유", "부문·점 공유"]
        _s_def  = (2 if (edit_task.get("shared_branch", False) if edit_task else False)
                   else (1 if (edit_task.get("shared", False) if edit_task else False) else 0))
        share_level   = st.radio("공유 범위", _s_opts, index=_s_def, horizontal=True)
        shared        = share_level != "비공개"
        shared_branch = share_level == "부문·점 공유"

        # 셀 선택 (팀장만)
        if is_manager:
            cell_keys = list(units.keys())
            default_cell = edit_task["cell"] if edit_task else cell_keys[0]
            cell_idx = cell_keys.index(default_cell) if default_cell in cell_keys else 0
            cell = st.selectbox("셀", cell_keys, format_func=lambda x: units[x]["name"], index=cell_idx)
        else:
            cell = user["cell"]

        s_col1, s_col2 = st.columns(2)
        submitted = s_col1.form_submit_button("저장", type="primary", use_container_width=True)
        cancelled = s_col2.form_submit_button("취소", use_container_width=True)

    if submitted and title.strip():
        task_data = {
            "title": title.strip(), "cell": cell, "pri": pri,
            "assignee": assignee, "due": due.isoformat(),
            "status": status, "desc": desc, "shared": shared, "shared_branch": shared_branch,
        }
        if edit_task:
            for t in st.session_state.tasks:
                if t["id"] == edit_id:
                    t.update(task_data)
                    break
            st.success("업무가 수정됐습니다!")
        else:
            task_data["id"] = new_id()
            st.session_state.tasks.append(task_data)
            st.success("업무가 추가됐습니다! 📅 캘린더에 자동 등록됩니다.")

        sync_tasks_to_calendar()
        st.session_state.show_task_modal = False
        st.rerun()

    if cancelled:
        st.session_state.show_task_modal = False
        st.rerun()
