"""
pages_modules/memo_view.py  — 메모장
"""
import streamlit as st
from datetime import date
from utils.state import get_visible_memos, new_id
from utils.ai_helper import extract_action_items, get_ai_memo_advice


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
                "cell":    None if user["cell"] in ("manager", "store_manager") else user["cell"],
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
        st.markdown("""
        <style>
        div[data-testid="stTextInput"] input {
            border: 1.5px solid #d1d5db !important;
            border-radius: 7px !important;
            background: #ffffff !important;
            padding: 8px 12px !important;
        }
        div[data-testid="stTextInput"] input:focus {
            border-color: #3b82f6 !important;
            box-shadow: 0 0 0 3px rgba(59,130,246,0.12) !important;
        }
        div[data-testid="stTextArea"] textarea {
            border: 1.5px solid #d1d5db !important;
            border-radius: 7px !important;
            background: #ffffff !important;
            padding: 10px 12px !important;
        }
        div[data-testid="stTextArea"] textarea:focus {
            border-color: #3b82f6 !important;
            box-shadow: 0 0 0 3px rgba(59,130,246,0.12) !important;
        }
        </style>
        """, unsafe_allow_html=True)

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
        col_share, col_save, col_ai, col_advice, col_del = st.columns([2, 1.2, 1.5, 1.5, 1])

        with col_share:
            _s_opts = ["비공개", "팀 공유", "점 공유"]
            _s_cur  = 2 if memo.get("shared_branch") else (1 if memo.get("shared") else 0)
            _s_new  = st.radio("공유", _s_opts, index=_s_cur, horizontal=True,
                                key=f"memo_share_{memo['id']}", label_visibility="collapsed")
            _new_shared = _s_new != "비공개"
            _new_branch = _s_new == "점 공유"
            if _new_shared != memo.get("shared") or _new_branch != memo.get("shared_branch"):
                memo["shared"]        = _new_shared
                memo["shared_branch"] = _new_branch
                st.toast("공유 설정이 변경됐습니다")

        with col_save:
            if st.button("💾 저장", use_container_width=True):
                memo["date"] = date.today().isoformat()
                if memo.get("content", "").strip():
                    with st.spinner("저장 & AI 조언 생성 중..."):
                        _adv = get_ai_memo_advice(
                            memo.get("title", "제목 없음"), memo["content"]
                        )
                    st.session_state[f"memo_advice_{memo['id']}"] = _adv
                st.toast("메모가 저장됐습니다!", icon="✅")
                st.rerun()

        with col_ai:
            if st.button("✦ Action 추출", use_container_width=True):
                if memo.get("content", "").strip():
                    with st.spinner("AI 분석 중..."):
                        result = extract_action_items(memo["content"])
                    st.session_state[f"action_result_{memo['id']}"] = result
                else:
                    st.toast("내용을 먼저 입력하세요.", icon="⚠️")

        with col_advice:
            if st.button("✦ AI 조언", use_container_width=True):
                if memo.get("content", "").strip():
                    with st.spinner("AI 분석 중..."):
                        _adv = get_ai_memo_advice(
                            memo.get("title", "제목 없음"), memo["content"]
                        )
                    st.session_state[f"memo_advice_{memo['id']}"] = _adv
                    st.rerun()
                else:
                    st.toast("내용을 먼저 입력하세요.", icon="⚠️")

        with col_del:
            if st.button("🗑 삭제", use_container_width=True):
                st.session_state.memos = [m for m in st.session_state.memos if m["id"] != cur_id]
                st.session_state.current_memo_id = None
                st.session_state.pop(f"action_result_{cur_id}", None)
                st.rerun()

        # ── AI 조언 표시 ────────────────────────────────────────
        memo_advice = st.session_state.get(f"memo_advice_{memo['id']}")
        if memo_advice:
            st.markdown(f"""
            <div style="margin-top:10px;background:linear-gradient(135deg,#0f172a,#0f3a2a);
                        border-radius:9px;padding:12px 15px">
              <div style="font-size:10.5px;letter-spacing:2px;font-weight:700;
                          color:rgba(255,255,255,0.6);margin-bottom:8px">✦ AI 조언</div>
              <div style="font-size:12.5px;color:rgba(255,255,255,0.9);line-height:1.8;
                          white-space:pre-wrap">{memo_advice}</div>
            </div>
            """, unsafe_allow_html=True)
            _adv_c1, _adv_c2 = st.columns(2)
            with _adv_c1:
                if st.button("↺ 재생성", key=f"regen_adv_{memo['id']}", use_container_width=True):
                    if memo.get("content", "").strip():
                        with st.spinner("AI 재생성 중..."):
                            st.session_state[f"memo_advice_{memo['id']}"] = get_ai_memo_advice(
                                memo.get("title", "제목 없음"), memo["content"]
                            )
                        st.rerun()
            with _adv_c2:
                if st.button("✕ 조언 닫기", key=f"close_adv_{memo['id']}", use_container_width=True):
                    st.session_state.pop(f"memo_advice_{memo['id']}", None)
                    st.rerun()

        # ── Action Items 표시 ────────────────────────────────
        action_result = st.session_state.get(f"action_result_{memo['id']}")
        if action_result:
            st.markdown("""
            <div style="margin-top:10px;background:linear-gradient(135deg,#0f172a,#1e3a5f);
                        border-radius:9px;padding:12px 15px">
              <div style="font-size:10.5px;letter-spacing:2px;font-weight:700;color:rgba(255,255,255,0.6);
                          margin-bottom:8px">✦ AI ACTION ITEMS</div>
            """, unsafe_allow_html=True)
            st.markdown(
                f"<div style='font-size:12.5px;color:rgba(255,255,255,0.9);line-height:1.8;"
                f"white-space:pre-wrap'>{action_result}</div>",
                unsafe_allow_html=True,
            )
            st.markdown("</div>", unsafe_allow_html=True)
            if st.button("✕ 닫기", key=f"close_action_{memo['id']}", use_container_width=True):
                st.session_state.pop(f"action_result_{memo['id']}", None)
                st.rerun()
