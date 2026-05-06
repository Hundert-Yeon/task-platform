"""
pages_modules/calendar_view.py
캘린더 페이지
"""
import streamlit as st
import calendar
from datetime import date, timedelta, datetime
from urllib.parse import quote
from utils.state import get_visible_events, new_id, KR_HOLIDAYS, EV_TYPES
from pages_modules.taskboard import _task_detail_popup

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


def _ical_escape(text: str) -> str:
    return str(text).replace("\\", "\\\\").replace(";", "\\;").replace(",", "\\,").replace("\n", "\\n")


def _generate_ics(events: list, cal_name: str = "영업기획팀 일정") -> bytes:
    """앱 이벤트 목록 → iCal(.ics) 파일 바이트 생성"""
    now_stamp = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    lines = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//롯데백화점 영업기획팀//Task Platform//KO",
        "CALSCALE:GREGORIAN",
        "METHOD:PUBLISH",
        f"X-WR-CALNAME:{_ical_escape(cal_name)}",
        "X-WR-TIMEZONE:Asia/Seoul",
    ]
    for ev in events:
        ds = ev.get("date", "")
        if not ds:
            continue
        try:
            d_start = date.fromisoformat(ds)
        except ValueError:
            continue
        d_end = d_start + timedelta(days=1)
        uid   = f"{ev.get('id', ds)}@task-platform"
        note  = _ical_escape(ev.get("note", "") or ev.get("desc", "") or "")
        lines += [
            "BEGIN:VEVENT",
            f"UID:{uid}",
            f"DTSTAMP:{now_stamp}",
            f"DTSTART;VALUE=DATE:{d_start.strftime('%Y%m%d')}",
            f"DTEND;VALUE=DATE:{d_end.strftime('%Y%m%d')}",
            f"SUMMARY:{_ical_escape(ev.get('title',''))}",
            f"DESCRIPTION:{note}",
            "END:VEVENT",
        ]
    lines.append("END:VCALENDAR")
    return "\r\n".join(lines).encode("utf-8")


def _gcal_link(ev: dict) -> str:
    """Google Calendar '일정 추가' 딥링크 생성 (종일 이벤트)"""
    ds = ev.get("date", "")
    if not ds:
        return ""
    try:
        d_start = date.fromisoformat(ds)
    except ValueError:
        return ""
    d_end   = d_start + timedelta(days=1)
    dates   = f"{d_start.strftime('%Y%m%d')}/{d_end.strftime('%Y%m%d')}"
    title   = quote(ev.get("title", ""))
    details = quote(ev.get("note", "") or ev.get("desc", "") or "")
    return (
        f"https://www.google.com/calendar/render?action=TEMPLATE"
        f"&text={title}&dates={dates}&details={details}"
    )


@st.dialog("일정 추가", width="large")
def _event_form_dialog():
    """일정 직접 추가 팝업"""
    with st.form("event_form_modal"):
        ev_title  = st.text_input("일정명 *")
        col1, col2 = st.columns(2)
        ev_date   = col1.date_input("날짜", value=date.today())
        ev_type   = col2.selectbox(
            "유형", list(EV_TYPES.keys()), format_func=lambda x: EV_TYPES[x]
        )
        ev_note   = st.text_input("메모")
        ev_shared = st.checkbox("전체 공유", value=True)

        s1, s2 = st.columns(2)
        submitted = s1.form_submit_button("저장", type="primary", use_container_width=True)
        cancelled = s2.form_submit_button("취소", use_container_width=True)

    if submitted and ev_title.strip():
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

    if cancelled:
        st.rerun()


def render():
    col_hdr, col_btn = st.columns([3, 1])
    with col_hdr:
        st.markdown("### 📅 캘린더")
        st.caption("팀 일정 · Task 마감일 자동 반영 · 공휴일 표기")
    with col_btn:
        st.write("")
        if st.button("＋ 일정 추가", type="primary", use_container_width=True, key="cal_add_ev_btn"):
            st.session_state.show_event_modal = True

    if st.session_state.get("show_event_modal"):
        _event_form_dialog()
        st.session_state.show_event_modal = False

    if "detail_task_id" not in st.session_state:
        st.session_state.detail_task_id = None

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
            if picked is not None:
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

        # 날짜 그리드 (버튼 기반 — 클릭으로 날짜 선택)
        for week in cal_matrix:
            week_cols = st.columns(7)
            for dow, day in enumerate(week):
                with week_cols[dow]:
                    if day == 0:
                        st.markdown(
                            "<div style='min-height:10px'></div>",
                            unsafe_allow_html=True,
                        )
                        continue

                    ds          = f"{yr}-{mo:02d}-{day:02d}"
                    is_today    = ds == today_str_val
                    is_selected = ds == sel_ds
                    is_holiday  = ds in KR_HOLIDAYS
                    is_sun      = dow == 0
                    is_sat      = dow == 6

                    # 클릭 버튼 (선택 날짜 = primary/파란색)
                    btn_type = "primary" if is_selected else "secondary"
                    if st.button(
                        str(day),
                        key=f"cal_day_{ds}",
                        use_container_width=True,
                        type=btn_type,
                    ):
                        st.session_state.cal_selected  = ds
                        st.session_state.cal_year      = int(ds[:4])
                        st.session_state.cal_month     = int(ds[5:7])
                        st.rerun()

                    # 날짜 정보 chips (오늘 표시 / 공휴일 / 이벤트)
                    evs = by_date.get(ds, [])
                    chips = ""
                    if is_today:
                        chips += (
                            "<div style='font-size:8px;color:#1d4ed8;"
                            "font-weight:700;text-align:center;margin:1px 0'>오늘</div>"
                        )
                    if is_holiday:
                        chips += (
                            f"<div style='font-size:8px;color:#dc2626;font-weight:600;"
                            f"white-space:nowrap;overflow:hidden;text-overflow:ellipsis'>"
                            f"{KR_HOLIDAYS[ds][:6]}</div>"
                        )
                    elif is_sun:
                        chips += (
                            "<div style='font-size:8px;color:#dc2626;"
                            "font-weight:600'>일</div>"
                        )
                    elif is_sat:
                        chips += (
                            "<div style='font-size:8px;color:#2563eb;"
                            "font-weight:600'>토</div>"
                        )
                    for ev in evs[:2]:
                        chips += (
                            f"<div style='font-size:8px;padding:1px 3px;border-radius:2px;"
                            f"background:{ev['color']}22;color:{ev['color']};font-weight:600;"
                            f"white-space:nowrap;overflow:hidden;text-overflow:ellipsis;"
                            f"margin:1px 0'>"
                            f"{ev['title'][:8]}{'…' if len(ev['title'])>8 else ''}</div>"
                        )
                    if len(evs) > 2:
                        chips += (
                            f"<div style='font-size:8px;color:#9ca3af'>+{len(evs)-2}개</div>"
                        )
                    if chips:
                        st.markdown(chips, unsafe_allow_html=True)

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

        def _task_card_html(ev, is_past=False):
            due_d      = date.fromisoformat(ev["date"])
            is_ov      = due_d < today
            is_soon    = today <= due_d <= in3
            is_sel_day = ev["date"] == sel_ds
            col        = "#9ca3af" if is_past else ("#dc2626" if is_ov else "#d97706" if is_soon else "#3b82f6")
            badge      = "⬜" if is_past else ("🔴" if is_ov else "🟡" if is_soon else "🔵")
            bc         = "#e5e7eb" if is_past else col
            hl_border  = "border:2px solid #1d4ed8;box-shadow:0 0 0 2px #dbeafe;" if is_sel_day and not is_past else ""
            text_col   = "#9ca3af" if is_past else "#111827"
            bg         = "#f9fafb" if is_past else ("#eff6ff" if is_sel_day else "white")
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
                f"background:{bg};border-radius:7px;border-left:3px solid {bc};"
                f"margin:4px 0;font-size:11.5px;{fade}{hl_border}'>"
                f"<span>{badge}</span>"
                f"<div style='flex:1;min-width:0'>"
                f"<div style='font-weight:600;color:{text_col};white-space:nowrap;"
                f"overflow:hidden;text-overflow:ellipsis;{strike}'>{ev['title']}</div>"
                f"<div style='display:flex;align-items:center;justify-content:space-between;margin-top:3px'>"
                f"<span style='font-size:10px;color:{col};font-family:monospace'>{ev['date']}</span>"
                f"{cell_badge}"
                f"</div></div></div>"
            )

        def _task_rows(ev_list, is_past=False):
            for ev in ev_list:
                st.markdown(_task_card_html(ev, is_past), unsafe_allow_html=True)
                task_id = ev.get("taskId")
                if task_id:
                    if st.button(
                        "📋 상세",
                        key=f"cal_tdet_{ev.get('id','')}{is_past}",
                        use_container_width=True,
                    ):
                        st.session_state.detail_task_id = task_id
                        st.rerun()

        if upcoming:
            _task_rows(upcoming, False)

        if past:
            st.markdown(
                "<div style='font-size:11px;color:#9ca3af;font-weight:600;"
                "margin:10px 0 4px;padding:5px 0;border-top:1px solid #f3f4f6'>"
                "⏰ 지나간 업무</div>",
                unsafe_allow_html=True,
            )
            _task_rows(past, True)

        if not task_evs:
            st.info("이달 등록된 Task 마감이 없습니다", icon="📭")

        st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)

        # Google Calendar 내보내기
        st.markdown(
            "<div style='font-size:13px;font-weight:700;color:#374151;margin-bottom:4px'>"
            "📤 Google Calendar 공유</div>",
            unsafe_allow_html=True,
        )
        st.caption("이 달 일정을 .ics 파일로 내보내거나, 개별 일정을 Google Calendar에 바로 추가할 수 있습니다.")

        # 이 달 전체 이벤트 → .ics 다운로드
        export_evs = [
            e for e in st.session_state.get("events", [])
            if e.get("date", "").startswith(f"{yr}-{mo:02d}")
        ]
        cfg_name   = st.session_state.cfg
        cal_label  = f"{cfg_name.get('branch_name','')} {cfg_name.get('team_name','')}".strip()
        ics_bytes  = _generate_ics(export_evs, cal_name=cal_label or "영업기획팀 일정")

        st.download_button(
            label=f"📥 {mo}월 일정 전체 다운로드 (.ics)",
            data=ics_bytes,
            file_name=f"{yr}{mo:02d}_영업기획팀.ics",
            mime="text/calendar",
            use_container_width=True,
            key="ics_download",
        )
        st.caption("다운로드 후 Google Calendar에서 **설정 → 가져오기**하거나, 파일을 열면 자동으로 추가됩니다.")

        # 선택된 날짜 개별 이벤트 → Google Calendar 직접 추가 링크
        day_manual_evs = [
            e for e in st.session_state.get("events", [])
            if e.get("date") == sel_ds and e.get("source") == "manual"
        ]
        if day_manual_evs:
            st.markdown(
                f"<div style='font-size:11.5px;font-weight:600;color:#374151;"
                f"margin:10px 0 4px'>📅 {sel_date.month}/{sel_date.day} 일정 바로 추가</div>",
                unsafe_allow_html=True,
            )
            for ev in day_manual_evs:
                link = _gcal_link(ev)
                if link:
                    st.markdown(
                        f"<a href='{link}' target='_blank' style='display:block;"
                        f"font-size:11px;padding:5px 9px;border-radius:6px;"
                        f"background:#f0fdf4;border:1px solid #bbf7d0;color:#065f46;"
                        f"text-decoration:none;margin:3px 0'>"
                        f"<span style='margin-right:5px'>📎</span>{ev['title']}</a>",
                        unsafe_allow_html=True,
                    )

    # ── 업무 상세 팝업 핸들러 ─────────────────────────────────
    if st.session_state.get("detail_task_id"):
        det_task = next(
            (t for t in st.session_state.tasks
             if t["id"] == st.session_state.detail_task_id),
            None,
        )
        if det_task:
            _task_detail_popup(det_task)
        st.session_state.detail_task_id = None
