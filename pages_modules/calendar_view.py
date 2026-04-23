"""
pages_modules/calendar_view.py
캘린더 페이지
"""
import streamlit as st
import calendar
from datetime import date, timedelta
from utils.state import get_visible_events, new_id, KR_HOLIDAYS, EV_TYPES

TYPE_COLORS = {
    "task":     "#3b82f6",
    "promo":    "#1d4ed8",
    "deadline": "#dc2626",
    "meeting":  "#059669",
    "holiday":  "#f59e0b",
    "etc":      "#7c3aed",
}

MKT_EVENTS = [
    ("2026-01-05", "소한"), ("2026-01-20", "대한"),
    ("2026-02-04", "입춘"), ("2026-02-14", "발렌타인데이"), ("2026-02-19", "우수"),
    ("2026-03-06", "경칩"), ("2026-03-14", "화이트데이"), ("2026-03-20", "춘분"),
    ("2026-04-05", "청명·식목일"), ("2026-04-20", "부활절"),
    ("2026-05-08", "어버이날"), ("2026-05-15", "스승의 날"), ("2026-05-21", "소만"),
    ("2026-06-06", "망종"), ("2026-06-18", "단오"), ("2026-06-21", "하지"),
    ("2026-06-25", "6.25 전쟁일"),
    ("2026-07-07", "소서"), ("2026-07-15", "초복"), ("2026-07-22", "대서"), ("2026-07-25", "중복"),
    ("2026-08-07", "입추"), ("2026-08-11", "말복"), ("2026-08-23", "처서"),
    ("2026-09-08", "백로"), ("2026-09-23", "추분"),
    ("2026-10-08", "한로"), ("2026-10-23", "상강"), ("2026-10-31", "핼러윈"),
    ("2026-11-07", "입동"), ("2026-11-11", "빼빼로데이"), ("2026-11-22", "소설"), ("2026-11-27", "블랙프라이데이"),
    ("2026-12-07", "대설"), ("2026-12-22", "동지"),
]


def render():
    st.markdown("### 📅 캘린더")
    st.caption("팀 일정 · Task 마감일 자동 반영 · 공휴일 표기")

    # 월 이동
    if "cal_year"  not in st.session_state: st.session_state.cal_year  = date.today().year
    if "cal_month" not in st.session_state: st.session_state.cal_month = date.today().month

    nav1, nav2, nav3 = st.columns([1, 3, 1])
    with nav1:
        if st.button("‹ 이전", use_container_width=True):
            if st.session_state.cal_month == 1:
                st.session_state.cal_year  -= 1
                st.session_state.cal_month  = 12
            else:
                st.session_state.cal_month -= 1
            st.rerun()
    with nav2:
        st.markdown(f"<h4 style='text-align:center;margin:0'>{st.session_state.cal_year}년 {st.session_state.cal_month}월</h4>", unsafe_allow_html=True)
    with nav3:
        if st.button("다음 ›", use_container_width=True):
            if st.session_state.cal_month == 12:
                st.session_state.cal_year  += 1
                st.session_state.cal_month  = 1
            else:
                st.session_state.cal_month += 1
            st.rerun()

    yr = st.session_state.cal_year
    mo = st.session_state.cal_month

    # 이벤트 맵 구성
    by_date: dict[str, list] = {}

    def add_ev(ds, ev):
        by_date.setdefault(ds, []).append(ev)

    for ds, name in KR_HOLIDAYS.items():
        add_ev(ds, {"title": name, "type": "holiday", "color": TYPE_COLORS["holiday"]})
    for ds, name in MKT_EVENTS:
        add_ev(ds, {"title": name, "type": "marketing", "color": "#e74c3c"})
    for ev in get_visible_events():
        col = TYPE_COLORS.get(ev.get("type","etc"), "#7c3aed")
        if ev.get("source") == "task":
            col = TYPE_COLORS["task"]
        add_ev(ev["date"], {"title": ev["title"], "type": ev.get("type","etc"), "color": col, "full": ev})

    # 캘린더 그리드 렌더링
    today_str = date.today().isoformat()
    cal_matrix = calendar.monthcalendar(yr, mo)

    # 요일 헤더
    headers = st.columns(7)
    day_names = ["일", "월", "화", "수", "목", "금", "토"]
    for i, h in enumerate(headers):
        color = "#dc2626" if i == 0 else "#2563eb" if i == 6 else "#374151"
        h.markdown(f"<div style='text-align:center;font-size:12px;font-weight:700;color:{color};padding:4px 0'>{h}</div>".replace(
            f"<div style='text-align:center;font-size:12px;font-weight:700;color:{color};padding:4px 0'>{h}</div>",
            f"<div style='text-align:center;font-size:12px;font-weight:700;color:{color};padding:4px 0'>{day_names[i]}</div>"
        ), unsafe_allow_html=True)

    for week in cal_matrix:
        week_cols = st.columns(7)
        for dow, day in enumerate(week):
            with week_cols[dow]:
                if day == 0:
                    st.markdown("<div style='min-height:80px;background:#f9fafb;border:1px solid #f3f4f6;border-radius:4px'></div>", unsafe_allow_html=True)
                    continue

                ds = f"{yr}-{mo:02d}-{day:02d}"
                is_today   = ds == today_str
                is_holiday = ds in KR_HOLIDAYS
                is_sun     = dow == 0
                is_sat     = dow == 6

                day_color = "#dc2626" if (is_holiday or is_sun) else "#2563eb" if is_sat else "#111827"
                bg_color  = "#dbeafe" if is_today else "#ffffff"
                border    = "2px solid #1d4ed8" if is_today else "1px solid #e5e7eb"

                evs = by_date.get(ds, [])
                chips_html = ""
                for ev in evs[:3]:
                    chips_html += f"""<div style="font-size:9px;padding:1px 4px;border-radius:3px;
                        background:{ev['color']}22;color:{ev['color']};font-weight:600;
                        white-space:nowrap;overflow:hidden;text-overflow:ellipsis;
                        margin:1px 0">{ev['title'][:10]}{'…' if len(ev['title'])>10 else ''}</div>"""
                if len(evs) > 3:
                    chips_html += f"<div style='font-size:9px;color:#9ca3af'>+{len(evs)-3}개</div>"

                holiday_label = f"<div style='font-size:9px;color:#dc2626;font-weight:600'>{KR_HOLIDAYS[ds]}</div>" if is_holiday else ""

                st.markdown(f"""
                <div style="min-height:85px;background:{bg_color};border:{border};
                            border-radius:5px;padding:3px 4px;overflow:hidden">
                  <div style="display:flex;align-items:flex-start;justify-content:space-between;margin-bottom:1px">
                    <span style="font-size:12px;font-weight:{'700' if is_today else '500'};color:{day_color if not is_today else '#1d4ed8'}">{day}</span>
                    {holiday_label}
                  </div>
                  {chips_html}
                </div>
                """, unsafe_allow_html=True)

    # ── 우측: Task 마감 패널 ──────────────────────────────────
    st.markdown("---")
    st.markdown("#### 📋 이달의 Task 마감")

    task_evs = [e for e in st.session_state.get("events", [])
                if e.get("source") == "task"
                and e.get("date", "").startswith(f"{yr}-{mo:02d}")]
    task_evs.sort(key=lambda e: e.get("date", ""))

    today = date.today()
    in3   = today + timedelta(days=3)

    if task_evs:
        for ev in task_evs:
            due_d   = date.fromisoformat(ev["date"])
            is_ov   = due_d < today
            is_soon = today <= due_d <= in3
            col     = "#dc2626" if is_ov else "#d97706" if is_soon else "#3b82f6"
            badge   = "🔴 지연" if is_ov else "🟡 임박" if is_soon else ""
            st.markdown(f"""
            <div style="display:flex;align-items:center;gap:10px;padding:8px 12px;
                        background:white;border-radius:7px;border:1.5px solid #e5e7eb;
                        border-left:3px solid {col};margin:4px 0;font-size:12.5px">
              <span style="flex:1">{ev['title']}</span>
              <span style="color:{col};font-family:monospace;font-size:11px">{ev['date']}</span>
              <span style="font-size:10px">{badge}</span>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("이달 등록된 Task 마감이 없습니다")

    # ── 일정 추가 ────────────────────────────────────────────
    st.markdown("---")
    with st.expander("➕ 일정 직접 추가"):
        with st.form("event_form"):
            ev_title  = st.text_input("일정명 *")
            col1, col2 = st.columns(2)
            ev_date   = col1.date_input("날짜", value=date.today())
            ev_type   = col2.selectbox("유형", list(EV_TYPES.keys()),
                                       format_func=lambda x: EV_TYPES[x])
            ev_note   = st.text_input("메모")
            ev_shared = st.checkbox("전체 공유", value=True)
            if st.form_submit_button("저장", type="primary"):
                if ev_title.strip():
                    user = st.session_state.user
                    st.session_state.events.append({
                        "id":     new_id(),
                        "title":  ev_title.strip(),
                        "date":   ev_date.isoformat(),
                        "type":   ev_type,
                        "note":   ev_note,
                        "shared": ev_shared,
                        "cell":   None if user["cell"] == "manager" else user["cell"],
                        "source": "manual",
                    })
                    st.success("일정이 추가됐습니다!")
                    st.rerun()
