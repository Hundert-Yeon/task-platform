"""
pages_modules/calendar_view.py
캘린더 페이지
"""
import re
import urllib.request
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
    "gcal":     "#e91e63",
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


def _fetch_ical(url: str) -> list:
    """Google Calendar iCal URL에서 이벤트를 파싱합니다"""
    if not url.strip():
        return []
    try:
        req = urllib.request.Request(url.strip(), headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=8) as r:
            raw = r.read().decode("utf-8", errors="ignore")
        raw = re.sub(r"\r?\n[ \t]", "", raw)
        events = []
        for block in re.split(r"BEGIN:VEVENT", raw)[1:]:
            block = block.split("END:VEVENT")[0]
            m_sum = re.search(r"^SUMMARY:(.+)$", block, re.MULTILINE)
            m_dt  = re.search(r"^DTSTART[^:]*:(\d{8})", block, re.MULTILINE)
            if m_sum and m_dt:
                summary = (m_sum.group(1).strip()
                           .replace("\\,", ",").replace("\\n", " ").replace("\\;", ";"))
                ds = m_dt.group(1)
                events.append({"title": summary, "date": f"{ds[:4]}-{ds[4:6]}-{ds[6:8]}"})
        return events
    except Exception:
        return []


def render():
    st.markdown("### 📅 캘린더")
    st.caption("팀 일정 · Task 마감일 자동 반영 · 공휴일 표기")

    today         = date.today()
    today_str_val = today.isoformat()

    if "cal_year"     not in st.session_state: st.session_state.cal_year     = today.year
    if "cal_month"    not in st.session_state: st.session_state.cal_month    = today.month
    if "cal_selected" not in st.session_state: st.session_state.cal_selected = today_str_val

    yr     = st.session_state.cal_year
    mo     = st.session_state.cal_month
    sel_ds = st.session_state.cal_selected

    # ── 이벤트 맵 구성 ────────────────────────────────────────
    by_date: dict[str, list] = {}

    def add_ev(ds, ev):
        by_date.setdefault(ds, []).append(ev)

    for ds, name in KR_HOLIDAYS.items():
        add_ev(ds, {"title": name, "type": "holiday", "color": TYPE_COLORS["holiday"]})
    for ds, name in MKT_EVENTS:
        add_ev(ds, {"title": name, "type": "marketing", "color": "#e74c3c"})
    for ev in get_visible_events():
        col = TYPE_COLORS.get(ev.get("type", "etc"), "#7c3aed")
        if ev.get("source") == "task":
            col = TYPE_COLORS["task"]
        add_ev(ev["date"], {"title": ev["title"], "type": ev.get("type", "etc"), "color": col, "full": ev})
    for ev in st.session_state.get("google_cal_events", []):
        add_ev(ev["date"], {"title": ev["title"], "type": "gcal", "color": TYPE_COLORS["gcal"]})

    # ── 2컬럼 레이아웃 ────────────────────────────────────────
    cal_col, side_col = st.columns([2, 1], gap="medium")

    with cal_col:
        # 월 네비게이션 + 날짜 선택기
        nav1, nav2, nav3, nav4 = st.columns([1, 2, 1, 2])
        with nav1:
            if st.button("‹ 이전", use_container_width=True, key="cal_prev"):
                if st.session_state.cal_month == 1:
                    st.session_state.cal_year  -= 1
                    st.session_state.cal_month  = 12
                else:
                    st.session_state.cal_month -= 1
                st.rerun()
        with nav2:
            st.markdown(
                f"<h4 style='text-align:center;margin:0;padding:6px 0'>{yr}년 {mo}월</h4>",
                unsafe_allow_html=True,
            )
        with nav3:
            if st.button("다음 ›", use_container_width=True, key="cal_next"):
                if st.session_state.cal_month == 12:
                    st.session_state.cal_year  += 1
                    st.session_state.cal_month  = 1
                else:
                    st.session_state.cal_month += 1
                st.rerun()
        with nav4:
            picked = st.date_input(
                "날짜 선택",
                value=date.fromisoformat(sel_ds),
                label_visibility="collapsed",
                key="cal_date_picker",
            )
            new_sel = picked.isoformat()
            if new_sel != sel_ds:
                st.session_state.cal_selected = new_sel
                st.session_state.cal_year  = picked.year
                st.session_state.cal_month = picked.month
                st.rerun()

        # 요일 헤더
        cal_matrix = calendar.monthcalendar(yr, mo)
        day_names  = ["일", "월", "화", "수", "목", "금", "토"]
        hdr_cols = st.columns(7)
        for i, hc in enumerate(hdr_cols):
            color = "#dc2626" if i == 0 else "#2563eb" if i == 6 else "#374151"
            hc.markdown(
                f"<div style='text-align:center;font-size:12px;font-weight:700;"
                f"color:{color};padding:4px 0'>{day_names[i]}</div>",
                unsafe_allow_html=True,
            )

        # 날짜 그리드
        for week in cal_matrix:
            week_cols = st.columns(7)
            for dow, day in enumerate(week):
                with week_cols[dow]:
                    if day == 0:
                        st.markdown(
                            "<div style='min-height:80px;background:#f9fafb;"
                            "border:1px solid #f3f4f6;border-radius:4px'></div>",
                            unsafe_allow_html=True,
                        )
                        continue

                    ds = f"{yr}-{mo:02d}-{day:02d}"
                    is_today    = ds == today_str_val
                    is_selected = ds == sel_ds
                    is_holiday  = ds in KR_HOLIDAYS
                    is_sun      = dow == 0
                    is_sat      = dow == 6

                    day_color = "#dc2626" if (is_holiday or is_sun) else "#2563eb" if is_sat else "#111827"

                    if is_today and is_selected:
                        bg_color      = "#dbeafe"
                        border        = "2px solid #1d4ed8"
                        day_fw        = "700"
                        day_color_val = "#1d4ed8"
                    elif is_selected:
                        bg_color      = "#f0fdf4"
                        border        = "2px solid #059669"
                        day_fw        = "700"
                        day_color_val = "#059669" if not (is_holiday or is_sun) else "#dc2626"
                    elif is_today:
                        bg_color      = "#eff6ff"
                        border        = "1px solid #93c5fd"
                        day_fw        = "600"
                        day_color_val = "#1d4ed8"
                    else:
                        bg_color      = "#ffffff"
                        border        = "1px solid #e5e7eb"
                        day_fw        = "500"
                        day_color_val = day_color

                    evs = by_date.get(ds, [])
                    chips_html = ""
                    for ev in evs[:3]:
                        chips_html += (
                            f"<div style='font-size:9px;padding:1px 4px;border-radius:3px;"
                            f"background:{ev['color']}22;color:{ev['color']};font-weight:600;"
                            f"white-space:nowrap;overflow:hidden;text-overflow:ellipsis;"
                            f"margin:1px 0'>{ev['title'][:10]}{'…' if len(ev['title'])>10 else ''}</div>"
                        )
                    if len(evs) > 3:
                        chips_html += f"<div style='font-size:9px;color:#9ca3af'>+{len(evs)-3}개</div>"

                    holiday_label = (
                        f"<div style='font-size:9px;color:#dc2626;font-weight:600'>{KR_HOLIDAYS[ds]}</div>"
                        if is_holiday else ""
                    )

                    st.markdown(
                        f"<div style='min-height:85px;background:{bg_color};border:{border};"
                        f"border-radius:5px;padding:3px 4px;overflow:hidden'>"
                        f"<div style='display:flex;align-items:flex-start;justify-content:space-between;margin-bottom:1px'>"
                        f"<span style='font-size:12px;font-weight:{day_fw};color:{day_color_val}'>{day}</span>"
                        f"{holiday_label}</div>{chips_html}</div>",
                        unsafe_allow_html=True,
                    )

    # ── 우측 사이드 패널 ──────────────────────────────────────
    with side_col:
        # 선택된 날짜 이벤트
        sel_date       = date.fromisoformat(sel_ds)
        kr_weekdays    = ["월", "화", "수", "목", "금", "토", "일"]
        wd             = kr_weekdays[sel_date.weekday()]
        is_sel_today   = sel_ds == today_str_val
        date_lbl_color = "#1d4ed8" if is_sel_today else "#059669"
        date_lbl_extra = " · 오늘" if is_sel_today else ""

        st.markdown(
            f"<div style='font-size:13px;font-weight:700;color:{date_lbl_color};margin-bottom:8px'>"
            f"📅 {sel_date.month}월 {sel_date.day}일 ({wd}){date_lbl_extra}</div>",
            unsafe_allow_html=True,
        )

        sel_evs = by_date.get(sel_ds, [])
        if sel_evs:
            sel_html = ""
            for ev in sel_evs:
                c = ev["color"]
                sel_html += (
                    f"<div style='font-size:11.5px;padding:5px 9px;border-radius:6px;"
                    f"background:{c}11;border-left:3px solid {c};margin:3px 0'>"
                    f"<span style='font-weight:600;color:{c}'>{ev['title']}</span>"
                    f"</div>"
                )
            st.markdown(sel_html, unsafe_allow_html=True)
        else:
            st.caption("이 날에 등록된 일정이 없습니다")

        st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

        # 이 달의 주요 업무
        st.markdown(
            "<div style='font-size:13px;font-weight:700;color:#374151;margin-bottom:8px'>"
            "📋 이 달의 주요 업무</div>",
            unsafe_allow_html=True,
        )

        task_evs = [
            e for e in st.session_state.get("events", [])
            if e.get("source") == "task"
            and e.get("date", "").startswith(f"{yr}-{mo:02d}")
        ]
        task_evs.sort(key=lambda e: e.get("date", ""))

        in3       = today + timedelta(days=3)
        cfg_units = st.session_state.cfg.get("units", {})

        upcoming = [e for e in task_evs if date.fromisoformat(e["date"]) >= today]
        past     = [e for e in task_evs if date.fromisoformat(e["date"]) < today]

        def _task_card(ev, is_past=False):
            due_d      = date.fromisoformat(ev["date"])
            is_ov      = due_d < today
            is_soon    = today <= due_d <= in3
            col        = "#9ca3af" if is_past else ("#dc2626" if is_ov else "#d97706" if is_soon else "#3b82f6")
            badge      = "⬜" if is_past else ("🔴" if is_ov else "🟡" if is_soon else "🔵")
            bc         = "#e5e7eb" if is_past else col
            text_col   = "#9ca3af" if is_past else "#111827"
            bg         = "#f9fafb" if is_past else "white"
            ci         = cfg_units.get(ev.get("cell", ""), {})
            cn         = ci.get("name", "")
            cc         = "#d1d5db" if is_past else ci.get("color", "#9ca3af")
            cell_badge = (
                f"<span style='font-size:9px;font-weight:700;padding:2px 7px;"
                f"border-radius:3px;background:{cc};color:white;flex-shrink:0'>{cn}</span>"
            ) if cn else ""
            strike = "text-decoration:line-through;" if is_past else ""
            fade   = "opacity:0.65;" if is_past else ""
            return (
                f"<div style='display:flex;align-items:flex-start;gap:6px;padding:7px 10px;"
                f"background:{bg};border-radius:7px;border:1px solid {bc};"
                f"border-left:3px solid {bc};margin:4px 0;font-size:11.5px;{fade}'>"
                f"<span>{badge}</span>"
                f"<div style='flex:1;min-width:0'>"
                f"<div style='font-weight:600;color:{text_col};white-space:nowrap;"
                f"overflow:hidden;text-overflow:ellipsis;{strike}'>{ev['title']}</div>"
                f"<div style='display:flex;align-items:center;justify-content:space-between;margin-top:3px'>"
                f"<span style='font-size:10px;color:{col};font-family:monospace'>{ev['date']}</span>"
                f"{cell_badge}"
                f"</div></div></div>"
            )

        if upcoming:
            st.markdown("".join(_task_card(e, False) for e in upcoming), unsafe_allow_html=True)

        if past:
            st.markdown(
                "<div style='font-size:11px;color:#9ca3af;font-weight:600;"
                "margin:10px 0 4px;padding:5px 0;border-top:1px solid #f3f4f6'>"
                "⏰ 지나간 업무</div>",
                unsafe_allow_html=True,
            )
            st.markdown("".join(_task_card(e, True) for e in past), unsafe_allow_html=True)

        if not task_evs:
            st.info("이달 등록된 Task 마감이 없습니다", icon="📭")

        st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)

        # Google Calendar 연동
        st.markdown(
            "<div style='font-size:13px;font-weight:700;color:#374151;margin-bottom:6px'>"
            "🔗 Google Calendar 연동</div>",
            unsafe_allow_html=True,
        )
        st.caption("Google Calendar → 설정 → 캘린더 통합 에서 iCal 주소를 복사하세요.")

        gcal_url = st.text_input(
            "iCal URL",
            value=st.session_state.get("google_cal_url", ""),
            placeholder="https://calendar.google.com/calendar/ical/...",
            label_visibility="collapsed",
            key="gcal_url_input",
        )

        btn_c1, btn_c2 = st.columns(2)
        with btn_c1:
            if st.button("🔄 연동하기", use_container_width=True, key="gcal_connect"):
                st.session_state.google_cal_url = gcal_url
                if gcal_url.strip():
                    with st.spinner("가져오는 중..."):
                        fetched = _fetch_ical(gcal_url)
                    st.session_state.google_cal_events = fetched
                    if fetched:
                        st.toast(f"✅ {len(fetched)}개 이벤트 연동됨")
                        st.rerun()
                    else:
                        st.toast("⚠️ 이벤트를 가져올 수 없습니다")
                else:
                    st.session_state.google_cal_events = []
        with btn_c2:
            if st.button("❌ 연동 해제", use_container_width=True, key="gcal_disconnect"):
                st.session_state.google_cal_url    = ""
                st.session_state.google_cal_events = []
                st.rerun()

        if st.session_state.get("google_cal_url", "").strip():
            n = len(st.session_state.get("google_cal_events", []))
            st.caption(f"✅ 연동 중 · 총 {n}개 이벤트")
        else:
            st.caption("미연동 상태")

    # ── 일정 직접 추가 ────────────────────────────────────────
    st.markdown("---")
    with st.expander("➕ 일정 직접 추가"):
        with st.form("event_form"):
            ev_title = st.text_input("일정명 *")
            col1, col2 = st.columns(2)
            ev_date  = col1.date_input("날짜", value=date.today())
            ev_type  = col2.selectbox("유형", list(EV_TYPES.keys()),
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
