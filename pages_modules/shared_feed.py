"""
pages_modules/shared_feed.py  — 전체 공유 피드
팀장: 현재 팀의 팀 공유 항목 / 점장: 전팀의 부문·점 공유 항목
"""
import streamlit as st


def render():
    user = st.session_state.user
    if user.get("cell") not in ("manager", "store_manager"):
        st.error("팀장 권한이 필요합니다.")
        return

    is_sm = user.get("cell") == "store_manager"

    st.markdown("### 🌐 전체 공유 피드")

    if is_sm:
        st.caption("부문·점 전체에 공유된 항목 (모든 팀)")
        teams_data = st.session_state.get("teams_data", {})

        all_tasks:  list[tuple] = []
        all_events: list[tuple] = []
        all_memos:  list[tuple] = []
        all_files:  list[tuple] = []

        for tid, td in teams_data.items():
            tcfg   = td["cfg"]
            tname  = tcfg.get("team_name", tid)
            tunits = tcfg.get("units", {})

            for t in td.get("tasks", []):
                if t.get("shared_branch"):
                    all_tasks.append((tname, tunits, t))
            for e in td.get("events", []):
                if e.get("shared_branch") and e.get("source") == "manual":
                    all_events.append((tname, tunits, e))
            for m in td.get("memos", []):
                if m.get("shared_branch"):
                    all_memos.append((tname, tunits, m))
            for f in td.get("files", []):
                if f.get("shared_branch"):
                    all_files.append((tname, tunits, f))

        total = len(all_tasks) + len(all_events) + len(all_memos) + len(all_files)
        st.info(f"🏢 부문·점 공유 항목 총 {total}개")
        _render_items(all_tasks, all_events, all_memos, all_files, show_team=True)

    else:
        st.caption("팀 전체 공유 항목")
        cfg   = st.session_state.cfg
        units = cfg.get("units", {})
        tname = cfg.get("team_name", "")

        tasks  = [(tname, units, t) for t in st.session_state.get("tasks", [])  if t.get("shared")]
        events = [(tname, units, e) for e in st.session_state.get("events", [])
                  if e.get("shared") and e.get("source") == "manual"]
        memos  = [(tname, units, m) for m in st.session_state.get("memos", [])  if m.get("shared")]
        files  = [(tname, units, f) for f in st.session_state.get("files", [])  if f.get("shared")]

        total = len(tasks) + len(events) + len(memos) + len(files)
        st.info(f"총 {total}개 항목이 공유됩니다")
        _render_items(tasks, events, memos, files, show_team=False)


def _render_items(tasks, events, memos, files, show_team: bool):
    total = len(tasks) + len(events) + len(memos) + len(files)

    if tasks:
        st.markdown("#### ✅ 공유된 Task")
        for tname, units, t in tasks:
            cell_name  = units.get(t.get("cell", ""), {}).get("name", t.get("cell", ""))
            cell_color = units.get(t.get("cell", ""), {}).get("color", "#999")
            share_ico  = "🏢" if t.get("shared_branch") else "🌐"
            team_tag   = (f"<span style='font-size:10px;color:#7c3aed;font-weight:700'>"
                          f"[{tname}]</span> " if show_team else "")
            st.markdown(f"""
            <div style="background:white;border-radius:7px;padding:10px 13px;
                        margin:4px 0;border:1.5px solid #e5e7eb;border-left:3px solid {cell_color}">
              <span style="font-weight:600">{t['title']}</span>
              <span style="float:right;font-size:11px;color:#9ca3af">{share_ico} {t.get('due','')}</span>
              <br>{team_tag}<span style="font-size:11px;color:{cell_color};font-weight:700">{cell_name}</span>
              &nbsp;<span style="font-size:11px;color:#6b7280">담당: {t.get('assignee','미정')}</span>
            </div>
            """, unsafe_allow_html=True)

    if events:
        st.markdown("#### 📅 공유된 일정")
        for tname, units, e in events:
            share_ico = "🏢" if e.get("shared_branch") else "🌐"
            team_tag  = (f"<span style='font-size:10px;color:#7c3aed;font-weight:700'>"
                         f"[{tname}]</span> " if show_team else "")
            st.markdown(f"""
            <div style="background:white;border-radius:7px;padding:10px 13px;
                        margin:4px 0;border:1.5px solid #e5e7eb;border-left:3px solid #d97706">
              <span style="font-weight:600">{e['title']}</span>
              <span style="float:right;font-size:11px;color:#9ca3af">{share_ico} {e.get('date','')}</span>
              <br>{team_tag}<span style="font-size:11px;color:#d97706">{e.get('note','')}</span>
            </div>
            """, unsafe_allow_html=True)

    if memos:
        st.markdown("#### 📝 공유된 메모")
        for tname, units, m in memos:
            cell_name = units.get(m.get("cell", ""), {}).get("name", "전체")
            share_ico = "🏢" if m.get("shared_branch") else "🌐"
            team_tag  = (f"<span style='font-size:10px;color:#7c3aed;font-weight:700'>"
                         f"[{tname}]</span> " if show_team else "")
            st.markdown(f"""
            <div style="background:white;border-radius:7px;padding:10px 13px;
                        margin:4px 0;border:1.5px solid #e5e7eb;border-left:3px solid #7c3aed">
              <span style="font-weight:600">{m['title']}</span>
              <span style="float:right;font-size:11px;color:#9ca3af">{share_ico} {m.get('date','')}</span>
              <br>{team_tag}<span style="font-size:11px;color:#6b7280">{cell_name}</span>
            </div>
            """, unsafe_allow_html=True)

    if files:
        st.markdown("#### 📁 공유된 파일")
        for tname, units, f in files:
            share_ico = "🏢" if f.get("shared_branch") else "🌐"
            team_tag  = f" [{tname}]" if show_team else ""
            st.markdown(f"""
            <div style="background:white;border-radius:7px;padding:10px 13px;
                        margin:4px 0;border:1.5px solid #e5e7eb;border-left:3px solid #3b82f6">
              <span style="font-weight:600">{share_ico} {f['name']}</span>
              <span style="float:right;font-size:11px;color:#9ca3af">{f.get('date','')}</span>
              <br><span style="font-size:11px;color:#6b7280">{f.get('size','')}{team_tag}</span>
            </div>
            """, unsafe_allow_html=True)

    if not total:
        st.info("공유된 항목이 없습니다")
