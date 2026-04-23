"""
pages_modules/memo_view.py  — 메모장
"""
import streamlit as st
from datetime import date
from utils.state import get_visible_memos, new_id
from utils.ai_helper import extract_action_items


def render():
    user = st.session_state.user
    st.markdown("### 📝 메모장")
    st.caption("회의록 · 인수인계 · 아이디어 기록")

    col_list, col_editor = st.columns([1, 2])

    with col_list:
        st.markdown("**메모 목록**")
        if st.button("+ 새 메모", use_container_width=True, type="primary"):
            new_memo = {
                "id":      new_id(),
                "title":   "새 메모",
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
            is_active = st.session_state.get("current_memo_id") == m["id"]
            shared_badge = " 🌐" if m.get("shared") else ""
            label = f"{'▶ ' if is_active else ''}{m['title'][:18]}{shared_badge}"
            if st.button(label, key=f"memo_sel_{m['id']}", use_container_width=True,
                         type="primary" if is_active else "secondary"):
                st.session_state.current_memo_id = m["id"]
                st.rerun()

    with col_editor:
        cur_id = st.session_state.get("current_memo_id")
        memo   = next((m for m in st.session_state.memos if m["id"] == cur_id), None)

        if not memo:
            st.info("왼쪽에서 메모를 선택하거나 새 메모를 만드세요.")
            return

        # 제목
        new_title = st.text_input("제목", value=memo["title"], key=f"memo_title_{memo['id']}")
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
            if st.button("✦ Action 추출", use_container_width=True):
                if memo["content"].strip():
                    with st.spinner("AI가 Action Item을 추출하는 중..."):
                        result = extract_action_items(memo["content"])
                    st.session_state[f"memo_ai_{memo['id']}"] = result
                else:
                    st.warning("메모 내용을 입력하세요")

        with col_del:
            if st.button("🗑 삭제", use_container_width=True):
                st.session_state.memos = [m for m in st.session_state.memos if m["id"] != cur_id]
                st.session_state.current_memo_id = None
                st.rerun()

        # AI 결과 표시
        ai_result = st.session_state.get(f"memo_ai_{memo['id']}")
        if ai_result:
            st.markdown("""
            <div style="background:linear-gradient(135deg,#eff6ff,#f5f3ff);
                        border-radius:8px;padding:12px 14px;margin-top:8px">
              <div style="font-size:11px;font-weight:700;color:#1d4ed8;margin-bottom:6px">✦ AI Action Items</div>
            """, unsafe_allow_html=True)
            st.text(ai_result)
            st.markdown("</div>", unsafe_allow_html=True)
