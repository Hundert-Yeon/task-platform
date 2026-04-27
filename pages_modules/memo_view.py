"""
pages_modules/memo_view.py  — 메모장
"""
import streamlit as st
from datetime import date
from utils.state import get_visible_memos, new_id


def render():
    user = st.session_state.user
    st.markdown("### 📝 메모장")
    st.caption("회의록 · 인수인계 · 아이디어 기록")

    col_list, col_editor = st.columns([1, 2])

    cfg_units = st.session_state.cfg.get("units", {})

    with col_list:
        st.markdown("**메모 목록**")
        if st.button("+ 새 메모", use_container_width=True, type="primary"):
            new_memo = {
                "id":      new_id(),
                "title":   "",
                "content": "",
                "date":    date.today().isoformat(),
                "cell":    None if user["cell"] == "manager" else user["cell"],
                "shared":  False,
            }
            st.session_state.memos.insert(0, new_memo)
            st.session_state.current_memo_id = new_memo["id"]
            st.rerun()

        memos = get_visible_memos()
        for m in memos:
            is_active    = st.session_state.get("current_memo_id") == m["id"]
            shared_badge = " 🌐" if m.get("shared") else ""
            cell_info    = cfg_units.get(m.get("cell", ""), {})
            cell_name    = cell_info.get("name", "")
            cell_color   = cell_info.get("color", "#9ca3af")
            display_title = m['title'][:18] if m['title'].strip() else "제목 없음"
            label = f"{'▶ ' if is_active else ''}{display_title}{shared_badge}"
            if st.button(label, key=f"memo_sel_{m['id']}", use_container_width=True,
                         type="primary" if is_active else "secondary"):
                st.session_state.current_memo_id = m["id"]
                st.rerun()
            if cell_name:
                st.markdown(
                    f"<div style='margin-top:-10px;margin-bottom:2px;padding-left:2px'>"
                    f"<span style='font-size:9px;font-weight:700;padding:1px 6px;"
                    f"border-radius:3px;background:{cell_color};color:white'>{cell_name}</span>"
                    f"</div>",
                    unsafe_allow_html=True,
                )

    with col_editor:
        cur_id = st.session_state.get("current_memo_id")
        memo   = next((m for m in st.session_state.memos if m["id"] == cur_id), None)

        if not memo:
            st.info("왼쪽에서 메모를 선택하거나 새 메모를 만드세요.")
            return

        # 소속 뱃지
        editor_cell_info  = cfg_units.get(memo.get("cell", ""), {})
        editor_cell_name  = editor_cell_info.get("name", "")
        editor_cell_color = editor_cell_info.get("color", "#9ca3af")
        if editor_cell_name:
            st.markdown(
                f"<div style='margin-bottom:6px'>"
                f"<span style='font-size:10px;font-weight:700;padding:3px 10px;"
                f"border-radius:4px;background:{editor_cell_color};color:white'>"
                f"{editor_cell_name}</span></div>",
                unsafe_allow_html=True,
            )

        # 제목
        new_title = st.text_input("제목", value=memo["title"], placeholder="제목을 입력하세요", key=f"memo_title_{memo['id']}")
        if new_title != memo["title"]:
            memo["title"] = new_title

        # 내용
        new_content = st.text_area("내용", value=memo["content"],
                                   height=280, key=f"memo_content_{memo['id']}")
        if new_content != memo["content"]:
            memo["content"]  = new_content
            memo["date"]     = date.today().isoformat()

        # 하단 툴바
        col_share, col_ai, col_del = st.columns([2, 2, 1])

        with col_share:
            shared = st.checkbox("🌐 전체 공유",
                                  value=memo.get("shared", False),
                                  key=f"memo_share_{memo['id']}")
            if shared != memo.get("shared"):
                memo["shared"] = shared
                msg = "전체 공유로 변경됐습니다" if shared else "공유가 해제됐습니다"
                st.toast(msg)

        with col_ai:
            if st.button("💾 저장", use_container_width=True):
                memo["date"] = date.today().isoformat()
                st.toast("메모가 저장됐습니다!", icon="✅")

        with col_del:
            if st.button("🗑 삭제", use_container_width=True):
                st.session_state.memos = [m for m in st.session_state.memos if m["id"] != cur_id]
                st.session_state.current_memo_id = None
                st.rerun()

        # AI 결과 표시
