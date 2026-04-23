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


def render():
    user  = st.session_state.user
    cfg   = st.session_state.cfg
    units = cfg.get("units", {})
    is_manager = user["cell"] == "manager"

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

    # ── 칸반 보드 ────────────────────────────────────────────
    today = date.today()
    in3   = today + timedelta(days=3)
    cols  = st.columns(4)

    for i, status in enumerate(STATUS_LIST):
        col_tasks = [t for t in visible if t["status"] == status["key"]]
        with cols[i]:
            st.markdown(f"""
            <div style="background:{status['color']};color:white;padding:8px 11px;
                        border-radius:8px 8px 0 0;font-size:12.5px;font-weight:700">
              {status['label']} &nbsp;<span style="opacity:.7">({len(col_tasks)})</span>
            </div>
            """, unsafe_allow_html=True)

            for t in col_tasks:
                due_d   = date.fromisoformat(t["due"]) if t.get("due") else None
                is_ov   = due_d and due_d < today and t["status"] != "done"
                is_soon = due_d and today <= due_d <= in3 and t["status"] != "done"
                due_color   = "#dc2626" if is_ov else "#d97706" if is_soon else "#9ca3af"
                pri_color   = PRIORITY_COLORS.get(t.get("pri","M"), "#9ca3af")
                cell_color  = units.get(t["cell"], {}).get("color", "#999")
                shared_border = "border-left:3px solid #059669;" if t.get("shared") else ""
                shared_ico  = " 🌐" if t.get("shared") else ""

                with st.container():
                    st.markdown(f"""
                    <div style="background:white;border-radius:8px;padding:11px 12px;
                                margin:5px 0;box-shadow:0 1px 4px rgba(0,0,0,0.07);
                                border-top:2px solid {pri_color};{shared_border}">
                      <div style="display:flex;align-items:flex-start;justify-content:space-between;margin-bottom:5px">
                        <span style="font-size:9px;font-weight:800;padding:2px 6px;border-radius:3px;
                                     background:{pri_color}22;color:{pri_color}">
                          {PRIORITY_LABELS.get(t.get('pri','M'),'보통')}
                        </span>
                        <span style="font-size:10px;color:#6b7280">{shared_ico}</span>
                      </div>
                      <div style="font-size:13px;font-weight:600;color:#111827;line-height:1.4;margin-bottom:7px">
                        {t['title']}
                      </div>
                      <div style="display:flex;align-items:center;gap:5px">
                        <span style="font-size:10px;font-weight:700;padding:2px 6px;border-radius:3px;
                                     background:{cell_color};color:white">
                          {units.get(t['cell'],{}).get('name', t['cell'])}
                        </span>
                        <span style="font-size:10px;color:{due_color};margin-left:auto;font-family:monospace">
                          ~{t.get('due','')}
                        </span>
                      </div>
                      <div style="font-size:10.5px;color:#6b7280;margin-top:5px">👤 {t.get('assignee','미정')}</div>
                    </div>
                    """, unsafe_allow_html=True)

                    # 수정/삭제 버튼
                    bc1, bc2, bc3 = st.columns([1, 1, 1])
                    with bc1:
                        if st.button("수정", key=f"edit_{t['id']}", use_container_width=True):
                            st.session_state.edit_task_id   = t["id"]
                            st.session_state.show_task_modal = True
                    with bc2:
                        new_st = _next_status(t["status"])
                        if new_st and st.button(f"→{new_st}", key=f"mv_{t['id']}", use_container_width=True):
                            t["status"] = new_st
                            sync_tasks_to_calendar()
                            st.rerun()
                    with bc3:
                        if st.button("삭제", key=f"del_{t['id']}", use_container_width=True):
                            st.session_state.tasks = [x for x in st.session_state.tasks if x["id"] != t["id"]]
                            sync_tasks_to_calendar()
                            st.rerun()

            # 컬럼 하단 추가 버튼
            if st.button(f"＋", key=f"add_col_{status['key']}", use_container_width=True):
                st.session_state.show_task_modal = True
                st.session_state.edit_task_id    = None
                st.session_state.default_status  = status["key"]

    # ── 업무 추가/수정 모달 ───────────────────────────────────
    if st.session_state.get("show_task_modal"):
        _task_form()


def _next_status(current: str) -> str | None:
    order = ["todo", "inprog", "done"]
    if current in order and order.index(current) < len(order) - 1:
        nxt = order[order.index(current) + 1]
        labels = {"todo":"대기","inprog":"진행","done":"완료"}
        return labels[nxt]
    return None


def _task_form():
    """업무 추가/수정 사이드 폼"""
    st.markdown("---")
    edit_id  = st.session_state.get("edit_task_id")
    edit_task = next((t for t in st.session_state.tasks if t["id"] == edit_id), None) if edit_id else None
    title_str = "업무 수정" if edit_task else "업무 추가"

    st.subheader(title_str)

    user  = st.session_state.user
    cfg   = st.session_state.cfg
    units = cfg.get("units", {})
    is_manager = user["cell"] == "manager"

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

        desc   = st.text_area("상세 내용", value=edit_task.get("desc","") if edit_task else "", height=70)
        shared = st.checkbox("전체 공유", value=edit_task.get("shared",False) if edit_task else False)

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
            "status": status, "desc": desc, "shared": shared,
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
