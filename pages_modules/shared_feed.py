"""
pages_modules/shared_feed.py  — 전체 공유 피드 (팀장 전용)
"""
import streamlit as st


def render():
    if st.session_state.user.get("cell") != "manager":
        st.error("팀장 권한이 필요합니다.")
        return

    cfg   = st.session_state.cfg
    units = cfg.get("units", {})

    st.markdown("### 🌐 전체 공유 피드")
    st.caption("팀원이 공유한 모든 항목")

    tasks  = [t for t in st.session_state.get("tasks", [])  if t.get("shared")]
    events = [e for e in st.session_state.get("events", []) if e.get("shared") and e.get("source") == "manual"]
    memos  = [m for m in st.session_state.get("memos", [])  if m.get("shared")]
    files  = [f for f in st.session_state.get("files", [])  if f.get("shared")]

    total = len(tasks) + len(events) + len(memos) + len(files)
    st.info(f"총 {total}개 항목이 공유됩니다")

    if tasks:
        st.markdown("#### ✅ 공유된 Task")
        for t in tasks:
            cell_name = units.get(t["cell"], {}).get("name", t["cell"])
            cell_color = units.get(t["cell"], {}).get("color", "#999")
            st.markdown(f"""
            <div style="background:white;border-radius:7px;padding:10px 13px;
                        margin:4px 0;border:1.5px solid #e5e7eb;border-left:3px solid {cell_color}">
              <span style="font-weight:600">{t['title']}</span>
              <span style="float:right;font-size:11px;color:#9ca3af">{t.get('due','')}</span>
              <br><span style="font-size:11px;color:{cell_color};font-weight:700">{cell_name}</span>
              &nbsp;<span style="font-size:11px;color:#6b7280">담당: {t.get('assignee','미정')}</span>
            </div>
            """, unsafe_allow_html=True)

    if events:
        st.markdown("#### 📅 공유된 일정")
        for e in events:
            st.markdown(f"""
            <div style="background:white;border-radius:7px;padding:10px 13px;
                        margin:4px 0;border:1.5px solid #e5e7eb;border-left:3px solid #d97706">
              <span style="font-weight:600">{e['title']}</span>
              <span style="float:right;font-size:11px;color:#9ca3af">{e.get('date','')}</span>
              <br><span style="font-size:11px;color:#d97706">{e.get('note','')}</span>
            </div>
            """, unsafe_allow_html=True)

    if memos:
        st.markdown("#### 📝 공유된 메모")
        for m in memos:
            cell_name  = units.get(m.get("cell",""), {}).get("name","전체")
            st.markdown(f"""
            <div style="background:white;border-radius:7px;padding:10px 13px;
                        margin:4px 0;border:1.5px solid #e5e7eb;border-left:3px solid #7c3aed">
              <span style="font-weight:600">{m['title']}</span>
              <span style="float:right;font-size:11px;color:#9ca3af">{m.get('date','')}</span>
              <br><span style="font-size:11px;color:#6b7280">{cell_name}</span>
            </div>
            """, unsafe_allow_html=True)

    if not total:
        st.info("공유된 항목이 없습니다")
