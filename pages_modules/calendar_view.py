"""
pages_modules/calendar_view.py
캘린더 페이지 — HTML 테이블 기반 Google Calendar 스타일
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
    now_stamp = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    lines = [
        "BEGIN:VCALENDAR", "VERSION:2.0",
        "PRODID:-//영업기획팀//Task Platform//KO",
        "CALSCALE:GREGORIAN", "METHOD:PUBLISH",
        f"X-WR-CALNAME:{_ical_escape(cal_name)}", "X-WR-TIMEZONE:Asia/Seoul",
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
        uid  = f"{ev.get('id', ds)}@task-platform"
        note = _ical_escape(ev.get("note", "") or "")
        lines += [
            "BEGIN:VEVENT", f"UID:{uid}", f"DTSTAMP:{now_stamp}",
            f"DTSTART;VALUE=DATE:{d_start.strftime('%Y%m%d')}",
            f"DTEND;VALUE=DATE:{d_end.strftime('%Y%m%d')}",
            f"SUMMARY:{_ical_escape(ev.get('title',''))}",
            f"DESCRIPTION:{note}", "END:VEVENT",
        ]
    lines.append("END:VCALENDAR")
    return "\r\n".join(lines).encode("utf-8")


def _gcal_link(ev: dict) -> str:
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
    details = quote(ev.get("note", "") or "")
    return (
        f"https://www.google.com/calendar/render?action=TEMPLATE"
        f"&text={title}&dates={dates}&details={details}"
    )


@st.dialog("일정 추가", width="large")
def _event_form_dialog():
    with st.form("event_form_modal"):
        ev_title  = st.text_input("일정명 *")
        col1, col2 = st.columns(2)
        ev_date   = col1.date_input("날짜", value=date.today())
        ev_type   = col2.selectbox("유형", list(EV_TYPES.keys()), format_func=lambda x: EV_TYPES[x])
        ev_note  = st.text_input("메모")
        _s_opts  = ["비공개", "팀 전체 공유", "부문·점 공유"]
        _s_level = st.radio("공유 범위", _s_opts, index=1, horizontal=True)
        ev_shared        = _s_level != "비공개"
        ev_shared_branch = _s_level == "부문·점 공유"
        s1, s2 = st.columns(2)
        submitted = s1.form_submit_button("저장", type="primary", use_container_width=True)
        cancelled = s2.form_submit_button("취소", use_container_width=True)
    if submitted and ev_title.strip():
        user = st.session_state.user
        st.session_state.events.append({
            "id": new_id(), "title": ev_title.strip(),
            "date": ev_date.isoformat(), "type": ev_type, "note": ev_note,
            "shared": ev_shared, "shared_branch": ev_shared_branch,
            "cell": None if user["cell"] in ("manager", "store_manager") else user["cell"],
            "source": "manual",
        })
        st.success("일정이 추가됐습니다!")
        st.rerun()
    if cancelled:
        st.rerun()


def _build_month_html(yr: int, mo: int, by_date: dict, sel_ds: str, today_str_val: str) -> str:
    """Google Calendar 스타일 월간 HTML 테이블 생성"""
    day_names  = ["일", "월", "화", "수", "목", "금", "토"]
    cal_matrix = calendar.monthcalendar(yr, mo)

    # 요일 헤더
    hdr_cells = ""
    for i, d in enumerate(day_names):
        color = "#dc2626" if i == 0 else "#2563eb" if i == 6 else "#374151"
        hdr_cells += (
            f"<th style='padding:5px 2px;font-size:11px;font-weight:700;"
            f"text-align:center;background:#f9fafb;border:1px solid #e5e7eb;"
            f"color:{color}'>{d}</th>"
        )

    # 날짜 행
    rows_html = ""
    for week in cal_matrix:
        cells_html = ""
        for dow, day in enumerate(week):
            if day == 0:
                cells_html += (
                    "<td style='border:1px solid #f0f0f0;background:#fafafa;"
                    "height:85px;vertical-align:top'></td>"
                )
                continue

            ds          = f"{yr}-{mo:02d}-{day:02d}"
            is_today    = ds == today_str_val
            is_sel      = ds == sel_ds
            is_holiday  = ds in KR_HOLIDAYS
            is_sun      = dow == 0
            is_sat      = dow == 6

            # 셀 배경·테두리
            if is_sel:
                td_style = (
                    "border:3px solid #1d4ed8;background:#eff6ff;"
                    "height:85px;vertical-align:top;padding:3px;"
                )
            elif is_today:
                td_style = (
                    "border:1px solid #93c5fd;background:#f0f7ff;"
                    "height:85px;vertical-align:top;padding:3px;"
                )
            else:
                td_style = (
                    "border:1px solid #e5e7eb;background:white;"
                    "height:85px;vertical-align:top;padding:3px;"
                )

            # 날짜 숫자 스타일
            if is_today:
                num_html = (
                    f"<a href='?cal_day={ds}' style='text-decoration:none;"
                    f"display:inline-flex;align-items:center;justify-content:center;"
                    f"width:22px;height:22px;border-radius:50%;"
                    f"background:#1d4ed8;color:white;"
                    f"font-size:11px;font-weight:800;flex-shrink:0'>{day}</a>"
                )
            elif is_holiday or is_sun:
                num_html = (
                    f"<a href='?cal_day={ds}' style='text-decoration:none;"
                    f"display:inline-flex;align-items:center;justify-content:center;"
                    f"width:22px;height:22px;border-radius:50%;"
                    f"color:#dc2626;"
                    f"font-size:11px;font-weight:700;flex-shrink:0'>{day}</a>"
                )
            elif is_sat:
                num_html = (
                    f"<a href='?cal_day={ds}' style='text-decoration:none;"
                    f"display:inline-flex;align-items:center;justify-content:center;"
                    f"width:22px;height:22px;border-radius:50%;"
                    f"color:#2563eb;"
                    f"font-size:11px;font-weight:700;flex-shrink:0'>{day}</a>"
                )
            else:
                num_html = (
                    f"<a href='?cal_day={ds}' style='text-decoration:none;"
                    f"display:inline-flex;align-items:center;justify-content:center;"
                    f"width:22px;height:22px;border-radius:50%;"
                    f"color:#374151;"
                    f"font-size:11px;font-weight:700;flex-shrink:0'>{day}</a>"
                )

            # 이벤트 바
            evs     = by_date.get(ds, [])
            ev_html = ""

            if is_holiday:
                ev_html += (
                    f"<div style='font-size:8px;color:#dc2626;font-weight:700;"
                    f"overflow:hidden;text-overflow:ellipsis;white-space:nowrap;"
                    f"margin:1px 0;line-height:1.3'>{KR_HOLIDAYS[ds][:7]}</div>"
                )

            mkt_evs = [e for e in evs if e["type"] == "marketing"]
            if mkt_evs:
                ev_html += (
                    f"<div style='font-size:8px;color:#e74c3c;"
                    f"overflow:hidden;text-overflow:ellipsis;white-space:nowrap;"
                    f"margin:1px 0;line-height:1.3'>▸{mkt_evs[0]['title'][:7]}</div>"
                )

            app_evs = [e for e in evs if e["type"] not in ("holiday", "marketing")]
            for ev in app_evs[:3]:
                t = ev["title"][:10] + ("…" if len(ev["title"]) > 10 else "")
                ev_html += (
                    f"<div style='font-size:8.5px;background:{ev['color']};color:white;"
                    f"font-weight:600;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;"
                    f"margin:1px 0;padding:1px 4px;border-radius:2px;line-height:1.4'>{t}</div>"
                )
            if len(app_evs) > 3:
                ev_html += (
                    f"<div style='font-size:7.5px;color:#9ca3af;margin:1px 0'>"
                    f"+{len(app_evs)-3}개 더보기</div>"
                )

            cells_html += (
                f"<td style='{td_style}'>"
                f"<div style='display:flex;justify-content:flex-end;margin-bottom:2px'>"
                f"{num_html}</div>"
                f"{ev_html}"
                f"</td>"
            )

        rows_html += f"<tr>{cells_html}</tr>"

    return (
        "<table style='width:100%;border-collapse:collapse;"
        "font-family:Noto Sans KR,sans-serif;table-layout:fixed'>"
        f"<thead><tr>{hdr_cells}</tr></thead>"
        f"<tbody>{rows_html}</tbody>"
        "</table>"
    )


def render():

    # ── 헤더 ─────────────────────────────────────────────────
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

    # ── query param 처리 (날짜 클릭) ────────────────────────
    q_day = st.query_params.get("cal_day", None)
    if q_day:
        try:
            q_d = date.fromisoformat(q_day)
            st.session_state.cal_selected = q_day
            st.session_state.cal_year     = q_d.year
            st.session_state.cal_month    = q_d.month
        except ValueError:
            pass
        st.query_params.clear()
        st.stop()

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
        add_ev(ev["date"], {
            "title": ev["title"], "type": ev.get("type", "etc"),
            "color": col, "full": ev,
        })

    # ── 2컬럼 레이아웃 ────────────────────────────────────────
    cal_col, side_col = st.columns([2, 1], gap="medium")

    with cal_col:
        # 월 네비게이션
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
                "날짜 선택", value=date.fromisoformat(sel_ds),
                label_visibility="collapsed", key="cal_date_picker",
            )
            if picked is not None:
                new_sel = picked.isoformat()
                if new_sel != sel_ds:
                    st.session_state.cal_selected = new_sel
                    st.session_state.cal_year  = picked.year
                    st.session_state.cal_month = picked.month
                    st.rerun()

        # HTML 캘린더 테이블 렌더링
        month_html = _build_month_html(yr, mo, by_date, sel_ds, today_str_val)
        st.markdown(month_html, unsafe_allow_html=True)

        # 오늘로 이동 버튼
        if st.button("오늘", key="cal_go_today", use_container_width=True):
            st.session_state.cal_selected = today_str_val
            st.session_state.cal_year     = today.year
            st.session_state.cal_month    = today.month
            st.rerun()

    # ── 우측 사이드 패널 ──────────────────────────────────────
    with side_col:
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

        # 선택된 날짜 이벤트 목록
        sel_evs = by_date.get(sel_ds, [])
        if sel_evs:
            sel_html = ""
            for ev in sel_evs:
                c = ev["color"]
                sel_html += (
                    f"<div style='font-size:11.5px;padding:5px 9px;border-radius:6px;"
                    f"background:{c}18;border-left:3px solid {c};margin:3px 0'>"
                    f"<span style='font-weight:600;color:{c}'>{ev['title']}</span></div>"
                )
            st.markdown(sel_html, unsafe_allow_html=True)
        else:
            st.caption("이 날에 등록된 일정이 없습니다")

        st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

        # ── 이 달의 주요 업무 ──────────────────────────────────
        st.markdown(
            "<div style='font-size:13px;font-weight:700;color:#374151;margin-bottom:6px'>"
            "📋 이 달의 주요 업무</div>",
            unsafe_allow_html=True,
        )

        task_evs = sorted(
            [
                e for e in st.session_state.get("events", [])
                if e.get("source") == "task"
                and e.get("date", "").startswith(f"{yr}-{mo:02d}")
            ],
            key=lambda e: e.get("date", ""),
        )

        in3       = today + timedelta(days=3)
        cfg_units = st.session_state.cfg.get("units", {})

        upcoming = [e for e in task_evs if date.fromisoformat(e["date"]) >= today]
        past     = [e for e in task_evs if date.fromisoformat(e["date"]) < today]

        def _task_rows(ev_list, is_past: bool = False):
            for ev in ev_list:
                task_id = ev.get("taskId")
                if not task_id:
                    continue
                due_d   = date.fromisoformat(ev["date"])
                is_ov   = due_d < today
                is_soon = today <= due_d <= in3
                ci      = cfg_units.get(ev.get("cell", ""), {})
                cn      = ci.get("name", "")

                badge   = "⬜" if is_past else ("🔴" if is_ov else "🟡" if is_soon else "🔵")
                title   = ev["title"].replace("[Task] ", "")
                l_color = "#d1d5db" if is_past else (
                    "#dc2626" if is_ov else "#d97706" if is_soon else "#3b82f6"
                )

                is_sel_task = ev["date"] == sel_ds
                card_bg     = "#eff6ff" if is_sel_task else ("#fafafa" if is_past else "white")
                fade        = "opacity:0.65;" if is_past else ""
                b_color     = "#1d4ed8" if is_sel_task else l_color
                bk          = f"calt{task_id.replace('-', '')}"

                hover_css = (
                    f".st-key-{bk} button:hover{{border-color:{b_color}!important;"
                    f"box-shadow:0 0 0 2px {b_color}!important;filter:brightness(0.96)!important;}}"
                ) if not is_past else ""

                st.markdown(
                    f"<style>"
                    f".st-key-{bk} button{{"
                    f"background:{card_bg}!important;"
                    f"border:1.5px solid {l_color}!important;"
                    f"border-left:3px solid {l_color}!important;"
                    f"border-radius:8px!important;text-align:left!important;"
                    f"padding:9px 12px!important;color:#1f2937!important;"
                    f"width:100%!important;margin:3px 0!important;"
                    f"font-size:12px!important;font-weight:600!important;"
                    f"cursor:pointer!important;height:auto!important;"
                    f"min-height:52px!important;white-space:normal!important;"
                    f"line-height:1.5!important;"
                    f"transition:border-color 0.15s,box-shadow 0.15s,filter 0.15s!important;"
                    f"{fade}}}"
                    f"{hover_css}"
                    f"</style>",
                    unsafe_allow_html=True,
                )

                btn_label = f"{badge} {title}\n📅 {ev['date']}"
                if cn:
                    btn_label += f"  · {cn}"

                if st.button(btn_label, key=bk, use_container_width=True):
                    det_task = next(
                        (t for t in st.session_state.tasks if t["id"] == task_id),
                        None,
                    )
                    if det_task:
                        _task_detail_popup(det_task)

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

        st.markdown("<div style='height:14px'></div>", unsafe_allow_html=True)

        # ── Google Calendar 내보내기 ──────────────────────────
        st.markdown(
            "<div style='font-size:13px;font-weight:700;color:#374151;margin-bottom:4px'>"
            "📤 Google Calendar 공유</div>",
            unsafe_allow_html=True,
        )
        export_evs = [
            e for e in st.session_state.get("events", [])
            if e.get("date", "").startswith(f"{yr}-{mo:02d}")
        ]
        cfg_name  = st.session_state.cfg
        cal_label = f"{cfg_name.get('branch_name','')} {cfg_name.get('team_name','')}".strip()
        ics_bytes = _generate_ics(export_evs, cal_name=cal_label or "영업기획팀 일정")

        st.download_button(
            label=f"📥 {mo}월 일정 전체 다운로드 (.ics)",
            data=ics_bytes,
            file_name=f"{yr}{mo:02d}_영업기획팀.ics",
            mime="text/calendar",
            use_container_width=True,
            key="ics_download",
        )

        day_manual_evs = [
            e for e in st.session_state.get("events", [])
            if e.get("date") == sel_ds and e.get("source") == "manual"
        ]
        if day_manual_evs:
            st.markdown(
                f"<div style='font-size:11.5px;font-weight:600;color:#374151;"
                f"margin:10px 0 4px'>📅 {sel_date.month}/{sel_date.day} Google Calendar 추가</div>",
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

    # ── 업무 상세 팝업 ────────────────────────────────────────
    if st.session_state.get("detail_task_id"):
        det_task = next(
            (t for t in st.session_state.tasks
             if t["id"] == st.session_state.detail_task_id),
            None,
        )
        if det_task:
            _task_detail_popup(det_task)
        st.session_state.detail_task_id = None
