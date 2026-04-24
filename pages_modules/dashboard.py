"""
pages_modules/dashboard.py
대시보드 페이지
"""
import re
import streamlit as st
from datetime import date, timedelta
from utils.state import (
    get_visible_tasks, STATUS_LIST, new_id, today_str, sync_tasks_to_calendar
)
from utils.ai_helper import get_ai_checklist

# 우선순위 색상 (HTML 프로토타입 기준)
PRIORITY_COLORS = {"H": "#dc2626", "M": "#d97706", "L": "#059669"}
PRIORITY_LABELS = {"H": "높음", "M": "보통", "L": "낮음"}
PRI_BG          = {"H": "#fee2e2", "M": "#fef3c7", "L": "#d1fae5"}
PRI_TEXT_COLOR  = {"H": "#b91c1c", "M": "#b45309", "L": "#065f46"}

LEVEL_COLORS = {"urgent": "#fca5a5", "normal": "#93c5fd", "ok": "#6ee7b7"}
LEVEL_LABELS = {"urgent": "긴급", "normal": "확인", "ok": "양호"}

AVATAR_COLORS = ["#1d4ed8","#059669","#7c3aed","#b45309","#dc2626","#0891b2","#be185d"]


def _esc(text: str) -> str:
    return str(text).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def _avatar_html(name: str) -> str:
    name = name or "?"
    color = AVATAR_COLORS[sum(ord(c) for c in name) % len(AVATAR_COLORS)]
    return (
        f'<span style="display:inline-flex;align-items:center;justify-content:center;'
        f'width:17px;height:17px;border-radius:4px;background:{color};color:white;'
        f'font-size:8.5px;font-weight:700;flex-shrink:0">{_esc(name[0])}</span>'
    )


def render():
    user  = st.session_state.user
    cfg   = st.session_state.cfg
    units = cfg.get("units", {})
    is_manager = user["cell"] == "manager"

    # ── view_cell 결정 ──────────────────────────────────────────
    if is_manager:
        unit_keys = list(units.keys())
        dash_cell = st.session_state.get("dash_cell", unit_keys[0] if unit_keys else "marketing")
        if dash_cell not in unit_keys:
            dash_cell = unit_keys[0]
        view_cell = dash_cell
    else:
        view_cell = user["cell"]

    title = f"{units.get(view_cell, {}).get('name', view_cell)} 대시보드"

    # ── 페이지 헤더: 타이틀(좌) + 업무 추가 버튼(우) ────────────
    col_title, col_btn = st.columns([3, 1])
    with col_title:
        st.markdown(f"### {title}")
        st.caption(date.today().strftime("%Y년 %m월 %d일 %A"))
    with col_btn:
        st.write("")
        if st.button("＋ 업무 추가", type="primary", use_container_width=True, key="dash_add_task"):
            st.session_state.show_task_form = True
            st.session_state.edit_task_id = None

    # ── 셀 탭 (팀장만) ─────────────────────────────────────────
    if is_manager:
        tab_cols = st.columns(len(unit_keys))
        for i, uk in enumerate(unit_keys):
            with tab_cols[i]:
                u = units[uk]
                if st.button(
                    f"{u.get('emoji','')} {u['name']}",
                    key=f"dash_cell_tab_{uk}",
                    type="primary" if uk == dash_cell else "secondary",
                    use_container_width=True,
                ):
                    st.session_state.dash_cell = uk
                    st.rerun()

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

    done = sum(1 for t in cell_tasks if t["status"] == "done")
    inp  = sum(1 for t in cell_tasks if t["status"] == "inprog")
    soon = sum(1 for t in cell_tasks
               if t["status"] != "done"
               and t.get("due", "") <= in3.isoformat()
               and t.get("due", "") >= today.isoformat())

    c1, c2, c3, c4 = st.columns(4)
    _stat_card(c1, "전체 Task",  len(cell_tasks), "이번 달 기준", "#3b82f6")
    _stat_card(c2, "진행 중",    inp,             "현재 처리 중", "#d97706")
    _stat_card(c3, "완료",       done,
               f"완료율 {int(done / max(len(cell_tasks), 1) * 100)}%", "#059669")
    _stat_card(c4, "마감 임박",  soon,            "3일 이내",     "#dc2626")

    # ── 칸반 보드 ────────────────────────────────────────────
    st.markdown(f"""
    <div style="display:flex;align-items:center;gap:8px;margin:16px 0 10px">
      <span style="font-size:11.5px;font-weight:700;color:#6b7280;
                   text-transform:uppercase;letter-spacing:0.8px">
        {_esc(units.get(view_cell, {}).get('name', view_cell))} 업무 현황
      </span>
      <div style="flex:1;height:1px;background:#e5e7eb"></div>
    </div>
    """, unsafe_allow_html=True)

    visible = [t for t in get_visible_tasks() if t["cell"] == view_cell]
    _render_kanban_html(visible, units)

    # ── 업무 추가 폼 ──────────────────────────────────────────
    if st.session_state.get("show_task_form"):
        _task_form(default_cell=view_cell)


# ─────────────────────────────────────────────────────────────
# 내부 렌더 함수
# ─────────────────────────────────────────────────────────────

def _stat_card(col, label: str, value: int, meta: str, color: str):
    col.markdown(f"""
    <div style="background:white;border-radius:10px;padding:12px 14px;
                border:1.5px solid #e5e7eb;border-top:3px solid {color};
                box-shadow:0 1px 3px rgba(0,0,0,0.07)">
      <div style="font-size:10.5px;color:#6b7280;font-weight:600;margin-bottom:6px">{_esc(label)}</div>
      <div style="font-size:26px;font-weight:700;color:#111827;font-family:monospace">{value}</div>
      <div style="font-size:10.5px;color:#d1d5db;margin-top:4px">{_esc(meta)}</div>
    </div>
    """, unsafe_allow_html=True)


def _render_kanban_html(tasks: list, units: dict):
    """대시보드 칸반 - 단일 HTML 블록으로 렌더링 (Streamlit 레이아웃 간섭 없음)"""
    today = date.today()
    in3   = today + timedelta(days=3)

    cols_html = ""
    for status in STATUS_LIST:
        col_tasks = [t for t in tasks if t["status"] == status["key"]]

        cards_html = ""
        for t in col_tasks:
            due_d     = date.fromisoformat(t["due"]) if t.get("due") else None
            is_ov     = due_d and due_d < today and t["status"] != "done"
            is_soon   = due_d and today <= due_d <= in3 and t["status"] != "done"
            due_color = "#dc2626" if is_ov else "#d97706" if is_soon else "#6b7280"
            pri       = t.get("pri", "M")
            ci        = units.get(t.get("cell", ""), {})
            cell_bg   = ci.get("color", "#9ca3af")
            cell_nm   = _esc(ci.get("name", t.get("cell", "")))
            shared_bl = "border-left:3px solid #059669;" if t.get("shared") else ""
            assignee  = t.get("assignee", "미정") or "미정"
            avatar    = _avatar_html(assignee)
            title     = _esc(t.get("title", ""))
            due_str   = _esc(t.get("due", ""))

            cards_html += f"""
            <div style="background:white;border-radius:7px;border:1.5px solid #e5e7eb;
                        padding:10px 11px;margin-bottom:6px;
                        box-shadow:0 1px 3px rgba(0,0,0,0.07);
                        border-top:2px solid {PRIORITY_COLORS.get(pri,'#d97706')};
                        {shared_bl}">
              <div style="display:flex;justify-content:space-between;
                          align-items:center;margin-bottom:6px">
                <span style="font-size:9px;font-weight:800;padding:2px 6px;
                             border-radius:3px;letter-spacing:.5px;
                             background:{PRI_BG.get(pri,'#fef3c7')};
                             color:{PRI_TEXT_COLOR.get(pri,'#b45309')}">
                  {PRIORITY_LABELS.get(pri,'보통')}
                </span>
                <span style="font-size:9.5px;font-weight:700;padding:2px 6px;
                             border-radius:3px;background:{cell_bg};color:white">
                  {cell_nm}
                </span>
              </div>
              <div style="font-size:12.5px;font-weight:600;color:#111827;
                          line-height:1.4;margin-bottom:6px">{title}</div>
              <div style="display:flex;align-items:center;justify-content:space-between">
                <span style="font-size:10px;color:{due_color};
                             font-family:monospace">~{due_str}</span>
                <div style="display:flex;align-items:center;gap:4px">
                  {avatar}
                  <span style="font-size:10.5px;color:#6b7280">{_esc(assignee)}</span>
                </div>
              </div>
            </div>
            """

        if not col_tasks:
            cards_html = (
                '<div style="text-align:center;color:#d1d5db;'
                'font-size:11px;padding:24px 0">업무 없음</div>'
            )

        cols_html += f"""
        <div style="background:#f8fafc;border-radius:10px;
                    border:1.5px solid #e5e7eb;overflow:hidden">
          <div style="padding:10px 12px;display:flex;align-items:center;gap:6px;
                      border-bottom:1.5px solid #e5e7eb">
            <span style="width:7px;height:7px;border-radius:50%;
                         background:{status['color']};display:inline-block;flex-shrink:0">
            </span>
            <span style="font-size:12px;font-weight:700;color:#111827;flex:1">
              {_esc(status['label'])}
            </span>
            <span style="font-size:10px;font-weight:700;background:#e5e7eb;
                         color:#6b7280;padding:1px 6px;border-radius:9px">
              {len(col_tasks)}
            </span>
          </div>
          <div style="padding:7px;min-height:60px">{cards_html}</div>
        </div>
        """

    full_html = (
        f'<div style="display:grid;grid-template-columns:repeat(4,1fr);'
        f'gap:12px;align-items:start">{cols_html}</div>'
    )
    full_html = re.sub(r'\n[ \t]*\n', '\n', full_html)
    st.markdown(full_html, unsafe_allow_html=True)


def _render_ai_checklist():
    st.markdown("""
    <div style="background:linear-gradient(135deg,#0f172a,#1e3a5f);
                border-radius:10px;padding:14px 16px;color:white">
      <div style="font-size:11px;letter-spacing:2px;font-weight:700;margin-bottom:10px">
        ✦ TODAY&#39;S AI CHECKLIST
      </div>
    """, unsafe_allow_html=True)

    cache_key = "ai_checklist_cache"
    if cache_key not in st.session_state:
        with st.spinner("AI 분석 중..."):
            st.session_state[cache_key] = get_ai_checklist()

    for item in st.session_state[cache_key]:
        level = item.get("level", "normal")
        color = LEVEL_COLORS.get(level, "#93c5fd")
        badge = LEVEL_LABELS.get(level, "확인")
        st.markdown(f"""
        <div style="background:rgba(255,255,255,0.07);border-radius:7px;
                    padding:7px 10px;margin:4px 0;display:flex;
                    align-items:flex-start;gap:8px;border:1px solid rgba(255,255,255,0.08)">
          <span style="font-size:13px;flex-shrink:0">{item.get('icon','📌')}</span>
          <span style="font-size:12px;color:rgba(255,255,255,0.85);
                       flex:1;line-height:1.5">{_esc(item.get('text',''))}</span>
          <span style="font-size:10px;font-weight:700;background:rgba(0,0,0,0.3);
                       color:{color};padding:2px 6px;border-radius:4px;
                       flex-shrink:0">{badge}</span>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

    if st.button("↺ 새로고침", key="refresh_checklist"):
        st.session_state.pop(cache_key, None)
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
            ci = units.get(t["cell"], {})
            items.append({
                "ico": "✅",
                "title": t["title"],
                "cell": ci.get("name", t["cell"]),
                "cell_color": ci.get("color", "#6b7280"),
            })
    for e in events:
        if e.get("shared") and e.get("source") == "manual":
            ci = units.get(e.get("cell", ""), {})
            items.append({
                "ico": "📅",
                "title": e["title"],
                "cell": ci.get("name", e.get("cell", "전체")) or "전체",
                "cell_color": ci.get("color", "#6b7280"),
            })
    for m in memos:
        if m.get("shared"):
            ci = units.get(m.get("cell", ""), {})
            items.append({
                "ico": "📝",
                "title": m["title"],
                "cell": ci.get("name", m.get("cell", "")),
                "cell_color": ci.get("color", "#6b7280"),
            })

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
        rows = ""
        for item in items[:10]:
            rows += f"""
            <div style="display:flex;align-items:center;gap:8px;padding:7px 12px;
                        border-bottom:1px solid #f3f4f6;font-size:12px">
              <span style="font-size:14px">{item['ico']}</span>
              <span style="flex:1;white-space:nowrap;overflow:hidden;
                           text-overflow:ellipsis;color:#374151">
                {_esc(item['title'])}
              </span>
              <span style="font-size:9px;font-weight:700;padding:2px 7px;
                           border-radius:3px;background:{item['cell_color']};
                           color:white;white-space:nowrap">
                {_esc(item['cell'])}
              </span>
            </div>
            """
        st.markdown(rows, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style="padding:24px;text-align:center;color:#9ca3af;font-size:12.5px">
          공유된 항목이 없습니다
        </div>""", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)


def _task_form(default_cell: str = "marketing"):
    cfg   = st.session_state.cfg
    units = cfg.get("units", {})
    user  = st.session_state.user

    st.markdown("---")
    st.subheader("업무 추가")

    with st.form("task_form"):
        title = st.text_input("업무명 *")
        col1, col2 = st.columns(2)
        with col1:
            pri = st.selectbox("우선순위", ["H", "M", "L"],
                               format_func=lambda x: PRIORITY_LABELS[x], index=1)
        with col2:
            status = st.selectbox(
                "상태", [s["key"] for s in STATUS_LIST],
                format_func=lambda x: next(s["label"] for s in STATUS_LIST if s["key"] == x)
            )
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
        st.session_state.tasks.append({
            "id":       new_id(),
            "title":    title.strip(),
            "cell":     cell,
            "pri":      pri,
            "assignee": assignee,
            "due":      due.isoformat(),
            "status":   status,
            "desc":     desc,
            "shared":   shared,
        })
        sync_tasks_to_calendar()
        st.session_state.show_task_form = False
        st.success("업무가 추가됐습니다!")
        st.rerun()

    if cancel:
        st.session_state.show_task_form = False
        st.rerun()
