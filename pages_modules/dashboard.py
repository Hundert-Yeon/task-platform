"""
pages_modules/dashboard.py
대시보드 페이지
"""
import streamlit as st
from datetime import date, timedelta
from utils.state import (
    get_visible_tasks, STATUS_LIST, new_id, today_str, sync_tasks_to_calendar
)
from utils.ai_helper import get_ai_checklist


PRIORITY_COLORS = {"H": "#dc2626", "M": "#d97706", "L": "#059669"}
PRIORITY_LABELS = {"H": "높음", "M": "보통", "L": "낮음"}
LEVEL_COLORS = {"urgent": "#fca5a5", "normal": "#93c5fd", "ok": "#6ee7b7"}
LEVEL_LABELS = {"urgent": "긴급", "normal": "확인", "ok": "양호"}


def render():
    user = st.session_state.user
    cfg  = st.session_state.cfg
    units = cfg.get("units", {})
    is_manager = user["cell"] == "manager"

    # 셀 선택 (팀장만)
    if is_manager:
        unit_keys = list(units.keys())
        dash_cell = st.session_state.get("dash_cell", unit_keys[0] if unit_keys else "marketing")
        selected = st.selectbox(
            "셀 선택",
            options=unit_keys,
            format_func=lambda x: units[x]["name"],
            index=unit_keys.index(dash_cell) if dash_cell in unit_keys else 0,
            key="dash_cell_select",
        )
        st.session_state.dash_cell = selected
        view_cell = selected
        title = f"{units[view_cell]['name']} 대시보드"
    else:
        view_cell = user["cell"]
        title = f"{units.get(view_cell, {}).get('name', view_cell)} 대시보드"

    st.markdown(f"### {title}")
    st.caption(date.today().strftime("%Y년 %m월 %d일 %A"))

    # ── 상단 2분할: 공유피드(좌) + AI 체크리스트(우) ──────────
    col_feed, col_ai = st.columns([1.15, 0.85])

    with col_feed:
        _render_shared_feed()

    with col_ai:
        _render_ai_checklist()

    st.divider()

    # ── 통계 카드 ────────────────────────────────────────────
    cell_tasks = [t for t in st.session_state.tasks if t["cell"] == view_cell]
    today = date.today()
    in3   = today + timedelta(days=3)

    done  = sum(1 for t in cell_tasks if t["status"] == "done")
    inp   = sum(1 for t in cell_tasks if t["status"] == "inprog")
    soon  = sum(1 for t in cell_tasks
                if t["status"] != "done"
                and t.get("due", "") <= in3.isoformat()
                and t.get("due", "") >= today.isoformat())

    c1, c2, c3, c4 = st.columns(4)
    _stat_card(c1, "전체 Task",  len(cell_tasks), "이번 달 기준",    "#3b82f6")
    _stat_card(c2, "진행 중",    inp,             "현재 처리 중",    "#d97706")
    _stat_card(c3, "완료",       done,            f"완료율 {int(done/max(len(cell_tasks),1)*100)}%", "#059669")
    _stat_card(c4, "마감 임박",  soon,            "3일 이내",        "#dc2626")

    # ── 칸반 보드 ────────────────────────────────────────────
    st.markdown("---")
    st.markdown(f"**{units.get(view_cell, {}).get('name', view_cell)} 업무 현황**")
    visible = [t for t in get_visible_tasks() if t["cell"] == view_cell]
    _render_kanban(visible, compact=True)

    # ── 업무 추가 버튼 ────────────────────────────────────────
    if st.button("+ 업무 추가", key="dash_add_task"):
        st.session_state.show_task_form = True
        st.session_state.edit_task_id   = None

    if st.session_state.get("show_task_form"):
        _task_form(default_cell=view_cell)


def _stat_card(col, label: str, value: int, meta: str, color: str):
    col.markdown(f"""
    <div style="background:white;border-radius:10px;padding:12px 14px;
                border:1.5px solid #e5e7eb;border-top:3px solid {color};
                box-shadow:0 1px 3px rgba(0,0,0,0.07)">
      <div style="font-size:10.5px;color:#6b7280;font-weight:600;margin-bottom:6px">{label}</div>
      <div style="font-size:26px;font-weight:700;color:#111827;font-family:monospace">{value}</div>
      <div style="font-size:10.5px;color:#d1d5db;margin-top:4px">{meta}</div>
    </div>
    """, unsafe_allow_html=True)


def _render_ai_checklist():
    st.markdown("""
    <div style="background:linear-gradient(135deg,#0f172a,#1e3a5f);
                border-radius:10px;padding:14px 16px;color:white;height:100%">
      <div style="font-size:11px;letter-spacing:2px;font-weight:700;margin-bottom:10px">
        ✦ TODAY&#39;S AI CHECKLIST
      </div>
    """, unsafe_allow_html=True)

    cache_key = "ai_checklist_cache"
    if cache_key not in st.session_state:
        with st.spinner("AI 분석 중..."):
            st.session_state[cache_key] = get_ai_checklist()

    items = st.session_state[cache_key]
    for item in items:
        level = item.get("level", "normal")
        color = LEVEL_COLORS.get(level, "#93c5fd")
        badge = LEVEL_LABELS.get(level, "확인")
        st.markdown(f"""
        <div style="background:rgba(255,255,255,0.07);border-radius:7px;
                    padding:7px 10px;margin:4px 0;display:flex;align-items:flex-start;gap:8px">
          <span style="font-size:13px">{item.get('icon','📌')}</span>
          <span style="font-size:12px;color:rgba(255,255,255,0.85);flex:1;line-height:1.5">{item.get('text','')}</span>
          <span style="font-size:10px;font-weight:700;background:rgba(0,0,0,0.3);
                       color:{color};padding:2px 6px;border-radius:4px;flex-shrink:0">{badge}</span>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

    if st.button("↺ 새로고침", key="refresh_checklist"):
        if cache_key in st.session_state:
            del st.session_state[cache_key]
        st.rerun()


def _render_shared_feed():
    tasks  = st.session_state.get("tasks", [])
    memos  = st.session_state.get("memos", [])
    events = st.session_state.get("events", [])
    cfg    = st.session_state.get("cfg", {})
    units  = cfg.get("units", {})

    items = []
    for t in tasks:
        if t.get("shared"):
            cell_name = units.get(t["cell"], {}).get("name", t["cell"])
            items.append({"ico": "✅", "title": t["title"], "cell": cell_name,
                          "sub": f"담당: {t.get('assignee','미정')} · 마감: {t.get('due','')}"})
    for e in events:
        if e.get("shared") and e.get("source") == "manual":
            cell_name = units.get(e.get("cell",""), {}).get("name", e.get("cell","전체"))
            items.append({"ico": "📅", "title": e["title"], "cell": cell_name or "전체",
                          "sub": f"{e['date']}"})
    for m in memos:
        if m.get("shared"):
            cell_name = units.get(m.get("cell",""), {}).get("name", m.get("cell",""))
            items.append({"ico": "📝", "title": m["title"], "cell": cell_name,
                          "sub": m.get("date","")})

    st.markdown(f"""
    <div style="background:white;border-radius:10px;border:1.5px solid #e5e7eb;
                box-shadow:0 1px 3px rgba(0,0,0,0.07);overflow:hidden">
      <div style="padding:10px 13px;border-bottom:1.5px solid #e5e7eb;background:#f9fafb;
                  display:flex;align-items:center;justify-content:space-between">
        <span style="font-size:12px;font-weight:700">🌐 전체 공유 피드</span>
        <span style="font-size:11px;color:#6b7280">{len(items)}건</span>
      </div>
    """, unsafe_allow_html=True)

    if items:
        for item in items[:10]:
            st.markdown(f"""
            <div style="display:flex;align-items:center;gap:8px;padding:7px 12px;
                        border-bottom:1px solid #f3f4f6;font-size:12px">
              <span>{item['ico']}</span>
              <span style="flex:1;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;color:#374151">{item['title']}</span>
              <span style="font-size:9.5px;color:#6b7280;white-space:nowrap">{item['cell']}</span>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style="padding:24px;text-align:center;color:#9ca3af;font-size:12.5px">
          공유된 항목이 없습니다
        </div>""", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)


def _render_kanban(tasks: list, compact: bool = False):
    cols = st.columns(4)
    today = date.today()
    in3   = today + timedelta(days=3)

    for i, status in enumerate(STATUS_LIST):
        col_tasks = [t for t in tasks if t["status"] == status["key"]]
        with cols[i]:
            st.markdown(f"""
            <div style="background:{status['color']};color:white;
                        padding:7px 10px;border-radius:7px 7px 0 0;
                        font-size:12px;font-weight:700;margin-bottom:4px">
              {status['label']} ({len(col_tasks)})
            </div>
            """, unsafe_allow_html=True)

            for t in col_tasks:
                due_d = date.fromisoformat(t["due"]) if t.get("due") else None
                is_ov = due_d and due_d < today and t["status"] != "done"
                is_soon = due_d and today <= due_d <= in3 and t["status"] != "done"
                due_color = "#dc2626" if is_ov else "#d97706" if is_soon else "#9ca3af"
                pri_color = PRIORITY_COLORS.get(t.get("pri","M"), "#9ca3af")
                shared_border = "border-left:3px solid #059669;" if t.get("shared") else ""

                st.markdown(f"""
                <div style="background:white;border-radius:7px;padding:10px 11px;
                            margin:4px 0;box-shadow:0 1px 3px rgba(0,0,0,0.06);
                            border-top:2px solid {pri_color};{shared_border}cursor:pointer">
                  <div style="font-size:12.5px;font-weight:600;color:#111827;
                              margin-bottom:5px;line-height:1.4">{t['title']}</div>
                  <div style="font-size:10px;color:{due_color};font-family:monospace">
                    ~{t.get('due','')}</div>
                  <div style="font-size:10.5px;color:#6b7280;margin-top:3px">
                    {t.get('assignee','미정')}</div>
                </div>
                """, unsafe_allow_html=True)

            # 업무 추가 버튼 (각 컬럼)
            if not compact:
                if st.button(f"+ 추가", key=f"add_{status['key']}"):
                    st.session_state.show_task_form = True
                    st.session_state.new_task_status = status["key"]


def _task_form(default_cell: str = "marketing"):
    """업무 추가/수정 폼"""
    cfg   = st.session_state.cfg
    units = cfg.get("units", {})
    user  = st.session_state.user

    st.markdown("---")
    st.subheader("업무 추가")

    with st.form("task_form"):
        title    = st.text_input("업무명 *")
        col1, col2 = st.columns(2)
        with col1:
            pri = st.selectbox("우선순위", ["H","M","L"],
                               format_func=lambda x: PRIORITY_LABELS[x], index=1)
        with col2:
            status = st.selectbox("상태", [s["key"] for s in STATUS_LIST],
                                  format_func=lambda x: next(s["label"] for s in STATUS_LIST if s["key"]==x))
        col3, col4 = st.columns(2)
        with col3:
            assignee = st.text_input("담당자", value=user["name"])
        with col4:
            due = st.date_input("마감일", value=date.today() + timedelta(days=7))
        desc   = st.text_area("상세 내용", height=80)
        shared = st.checkbox("전체 공유 (체크 시 전 팀원에게 공개)")

        submitted = st.form_submit_button("저장", type="primary")
        cancel    = st.form_submit_button("취소")

    if submitted and title.strip():
        cell = default_cell if user["cell"] == "manager" else user["cell"]
        new_task = {
            "id":       new_id(),
            "title":    title.strip(),
            "cell":     cell,
            "pri":      pri,
            "assignee": assignee,
            "due":      due.isoformat(),
            "status":   status,
            "desc":     desc,
            "shared":   shared,
        }
        st.session_state.tasks.append(new_task)
        sync_tasks_to_calendar()
        st.session_state.show_task_form = False
        st.success("업무가 추가됐습니다!")
        st.rerun()

    if cancel:
        st.session_state.show_task_form = False
        st.rerun()
