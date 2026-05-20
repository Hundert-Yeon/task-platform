"""
pages_modules/dashboard.py
대시보드 페이지
"""
import streamlit as st
from datetime import date, timedelta
from utils.state import get_visible_tasks, STATUS_LIST
from utils.ai_helper import get_ai_checklist
from pages_modules.taskboard import _task_form, _task_detail_popup

# 우선순위 색상 (HTML 프로토타입 기준)
PRIORITY_COLORS = {"H": "#dc2626", "M": "#d97706", "L": "#059669"}
PRIORITY_LABELS = {"H": "높음", "M": "보통", "L": "낮음"}
PRI_BG          = {"H": "#fee2e2", "M": "#fef3c7", "L": "#d1fae5"}
PRI_TEXT_COLOR  = {"H": "#b91c1c", "M": "#b45309", "L": "#065f46"}

LEVEL_COLORS = {"urgent": "#fca5a5", "normal": "#93c5fd", "ok": "#6ee7b7"}
LEVEL_LABELS = {"urgent": "긴급", "normal": "확인", "ok": "양호"}


def _esc(text: str) -> str:
    return str(text).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")



def render():
    user  = st.session_state.user
    cfg   = st.session_state.cfg
    units = cfg.get("units", {})
    is_manager = user["cell"] in ("manager", "store_manager")

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
            st.session_state.show_task_modal = True
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

    if "detail_task_id" not in st.session_state:
        st.session_state.detail_task_id = None

    visible = [t for t in get_visible_tasks() if t["cell"] == view_cell]

    # ── AI 조언 사전 생성 (캐시 없는 Task만) ────────────────
    from utils.ai_helper import get_ai_task_advice, get_client
    _need = [t for t in visible if not st.session_state.get(f"task_advice_{t['id']}")]
    if _need and get_client():
        with st.spinner(f"AI 조언 생성 중... ({len(_need)}건)"):
            for _t in _need:
                _k = f"task_advice_{_t['id']}"
                if not st.session_state.get(_k):
                    try:
                        st.session_state[_k] = get_ai_task_advice(_t)
                    except Exception:
                        pass

    _render_kanban(visible, units)

    # ── 팝업 핸들러 ──────────────────────────────────────────
    if st.session_state.get("detail_task_id"):
        det_task = next(
            (t for t in st.session_state.tasks
             if t["id"] == st.session_state.detail_task_id),
            None,
        )
        if det_task:
            _task_detail_popup(det_task)
        st.session_state.detail_task_id = None

    if st.session_state.get("show_task_modal"):
        _task_form()
        st.session_state.show_task_modal = False


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


def _render_kanban(tasks: list, units: dict):
    """대시보드 칸반 - 인터랙티브 버전 (상세 팝업 지원)"""
    today = date.today()
    in3   = today + timedelta(days=3)

    cols = st.columns(4)
    for i, status in enumerate(STATUS_LIST):
        col_tasks = [t for t in tasks if t["status"] == status["key"]]
        with cols[i]:
            st.markdown(
                f"<div style='background:{status['color']};color:white;padding:8px 11px;"
                f"border-radius:8px 8px 0 0;font-size:12.5px;font-weight:700'>"
                f"{status['label']} "
                f"<span style='opacity:.7'>({len(col_tasks)})</span></div>",
                unsafe_allow_html=True,
            )

            for t in col_tasks:
                due_d      = date.fromisoformat(t["due"]) if t.get("due") else None
                is_ov      = due_d and due_d < today and t["status"] != "done"
                is_soon    = due_d and today <= due_d <= in3 and t["status"] != "done"
                due_color  = "#dc2626" if is_ov else "#d97706" if is_soon else "#9ca3af"
                pri        = t.get("pri", "M")
                pri_color  = PRIORITY_COLORS.get(pri, "#d97706")
                ci         = units.get(t.get("cell", ""), {})
                cell_bg    = ci.get("color", "#9ca3af")
                cell_nm    = ci.get("name", t.get("cell", ""))
                shared_bl  = ("border-left:3px solid #7c3aed;" if t.get("shared_branch")
                              else ("border-left:3px solid #059669;" if t.get("shared") else ""))
                assignee   = t.get("assignee", "미정") or "미정"

                _bk = f"dashcard{t['id']}"
                _pri_dot = {"H": "🔴", "M": "🟡", "L": "🟢"}.get(pri, "🟡")
                _shared_bl_color = (
                    "#7c3aed" if t.get("shared_branch")
                    else ("#059669" if t.get("shared") else "#e5e7eb")
                )
                _sh_ico = (
                    " 🏢" if t.get("shared_branch") else (" 🌐" if t.get("shared") else "")
                )

                st.markdown(
                    f"<style>"
                    f".st-key-{_bk} button{{"
                    f"background:white!important;"
                    f"border-top:2px solid {pri_color}!important;"
                    f"border-left:3px solid {_shared_bl_color}!important;"
                    f"border-right:1px solid #e5e7eb!important;"
                    f"border-bottom:1px solid #e5e7eb!important;"
                    f"border-radius:8px!important;text-align:left!important;"
                    f"padding:9px 12px 10px!important;width:100%!important;"
                    f"margin:5px 0!important;box-shadow:0 1px 4px rgba(0,0,0,0.07)!important;"
                    f"cursor:pointer!important;height:auto!important;"
                    f"white-space:pre-wrap!important;line-height:1.75!important;"
                    f"font-size:12.5px!important;font-weight:600!important;"
                    f"color:#111827!important;word-break:keep-all!important;"
                    f"transition:box-shadow 0.15s,transform 0.15s!important;}}"
                    f".st-key-{_bk} button:hover{{"
                    f"box-shadow:0 4px 14px rgba(0,0,0,0.13)!important;"
                    f"transform:translateY(-1px)!important;}}"
                    f"</style>",
                    unsafe_allow_html=True,
                )

                _btn_lbl = (
                    f"{_pri_dot} {PRIORITY_LABELS.get(pri,'보통')}  ·  {cell_nm}{_sh_ico}\n"
                    f"{t.get('title', '')}\n"
                    f"마감 ~{t.get('due', '')}  ·  👤 {assignee}"
                )

                if st.button(_btn_lbl, key=_bk, use_container_width=True):
                    st.session_state.detail_task_id = t["id"]
                    st.rerun()

                # ── AI 조언 (최대 2개) ────────────────────────
                _adv = st.session_state.get(f"task_advice_{t['id']}")
                if _adv and isinstance(_adv, list):
                    _LVLC = {"urgent": "#fca5a5", "normal": "#93c5fd", "ok": "#6ee7b7"}
                    _LVLL = {"urgent": "긴급", "normal": "확인", "ok": "양호"}
                    _rows = ""
                    for _it in _adv[:2]:
                        _lv = _it.get("level", "normal")
                        _rows += (
                            f"<div style='background:rgba(255,255,255,0.07);border-radius:6px;"
                            f"padding:5px 8px;margin:2px 0;display:flex;align-items:flex-start;"
                            f"gap:6px;border:1px solid rgba(255,255,255,0.08)'>"
                            f"<span style='font-size:11px;flex-shrink:0'>{_it.get('icon','📌')}</span>"
                            f"<span style='font-size:10.5px;color:rgba(255,255,255,0.9);"
                            f"flex:1;line-height:1.45'>{_esc(str(_it.get('text','')))}</span>"
                            f"<span style='font-size:9px;font-weight:700;background:rgba(0,0,0,0.3);"
                            f"color:{_LVLC.get(_lv,'#93c5fd')};padding:1px 4px;border-radius:3px;"
                            f"flex-shrink:0'>{_LVLL.get(_lv,'확인')}</span>"
                            f"</div>"
                        )
                    if _rows:
                        st.markdown(
                            f"<div style='background:linear-gradient(135deg,#0f172a,#1e3a5f);"
                            f"border-radius:7px;padding:8px 10px;margin:2px 0 4px'>"
                            f"<div style='font-size:9px;letter-spacing:1.5px;font-weight:700;"
                            f"color:rgba(255,255,255,0.45);margin-bottom:4px'>✦ AI 조언</div>"
                            f"{_rows}</div>",
                            unsafe_allow_html=True,
                        )

            if not col_tasks:
                st.markdown(
                    "<div style='text-align:center;color:#d1d5db;"
                    "font-size:11px;padding:24px 0;background:#f8fafc;"
                    "border-radius:0 0 8px 8px'>업무 없음</div>",
                    unsafe_allow_html=True,
                )


def _render_ai_checklist():
    cache_key = "ai_checklist_cache"
    if cache_key not in st.session_state:
        with st.spinner("AI 분석 중..."):
            st.session_state[cache_key] = get_ai_checklist()

    checklist = st.session_state[cache_key]
    if not isinstance(checklist, list):
        checklist = [{"icon": "⚠️", "text": "체크리스트를 불러오는 중 문제가 발생했습니다.", "level": "urgent"}]

    items_html = ""
    for item in checklist:
        level = item.get("level", "normal")
        color = LEVEL_COLORS.get(level, "#93c5fd")
        badge = LEVEL_LABELS.get(level, "확인")
        items_html += (
            f"<div style='background:rgba(255,255,255,0.07);border-radius:7px;"
            f"padding:7px 10px;margin:4px 0;display:flex;"
            f"align-items:flex-start;gap:8px;border:1px solid rgba(255,255,255,0.08)'>"
            f"<span style='font-size:13px;flex-shrink:0'>{item.get('icon','📌')}</span>"
            f"<span style='font-size:12px;color:rgba(255,255,255,0.9);"
            f"flex:1;line-height:1.5'>{_esc(item.get('text',''))}</span>"
            f"<span style='font-size:10px;font-weight:700;background:rgba(0,0,0,0.3);"
            f"color:{color};padding:2px 6px;border-radius:4px;"
            f"flex-shrink:0'>{badge}</span>"
            f"</div>"
        )

    if not items_html:
        items_html = (
            "<div style='color:rgba(255,255,255,0.5);font-size:12px;"
            "text-align:center;padding:16px'>항목이 없습니다</div>"
        )

    full_html = (
        "<div style='background:linear-gradient(135deg,#0f172a,#1e3a5f);"
        "border-radius:10px;padding:14px 16px;color:white'>"
        "<div style='font-size:11px;letter-spacing:2px;font-weight:700;margin-bottom:10px'>"
        "✦ TODAY'S AI CHECKLIST"
        "</div>"
        f"{items_html}"
        "</div>"
    )
    st.markdown(full_html, unsafe_allow_html=True)

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


