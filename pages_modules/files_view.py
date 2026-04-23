"""
pages_modules/files_view.py  — 파일 저장소
"""
import streamlit as st
from datetime import date
from utils.state import new_id


FOLDER_MAP = {
    "all":    ("🗂️", "전체"),
    "crm":    ("📊", "CRM분석"),
    "promo":  ("🎯", "프로모션"),
    "md":     ("🏷️", "MD기획"),
    "report": ("📋", "보고서"),
    "etc":    ("📦", "기타"),
}

ICONS = {
    "pdf": "📄", "xlsx": "📊", "pptx": "📑", "docx": "📝",
    "jpg": "🖼️", "png": "🖼️", "zip": "📦",
}


def _fmt_bytes(b: int) -> str:
    if b < 1024:      return f"{b}B"
    if b < 1048576:   return f"{b/1024:.1f}KB"
    return f"{b/1048576:.1f}MB"


def render():
    user  = st.session_state.user
    cfg   = st.session_state.cfg
    units = cfg.get("units", {})

    st.markdown("### 📁 파일 저장소")
    st.caption("유닛/셀별 문서 관리 · 업로드/다운로드")

    col_folder, col_main = st.columns([1, 3])

    with col_folder:
        st.markdown("**폴더**")
        cur_folder = st.session_state.get("cur_folder", "all")
        for fk, (ico, fname) in FOLDER_MAP.items():
            is_active = cur_folder == fk
            if st.button(f"{ico} {fname}", key=f"folder_{fk}",
                         use_container_width=True,
                         type="primary" if is_active else "secondary"):
                st.session_state.cur_folder = fk
                st.rerun()

    with col_main:
        cur_folder = st.session_state.get("cur_folder", "all")
        query      = st.text_input("🔍 파일 검색", placeholder="파일명 검색...")

        # 파일 업로드
        uploaded = st.file_uploader("파일 업로드", accept_multiple_files=True, label_visibility="collapsed")
        if uploaded:
            for f in uploaded:
                folder = cur_folder if cur_folder != "all" else "etc"
                st.session_state.files.append({
                    "id":     new_id(),
                    "name":   f.name,
                    "size":   _fmt_bytes(f.size),
                    "date":   date.today().isoformat(),
                    "folder": folder,
                    "cell":   None if user["cell"] == "manager" else user["cell"],
                    "tags":   [folder],
                    "shared": False,
                })
            st.success(f"{len(uploaded)}개 파일이 업로드됐습니다!")
            st.rerun()

        # 파일 목록 표시
        files = st.session_state.get("files", [])
        is_manager = user["cell"] == "manager"
        visible = [
            f for f in files
            if (is_manager or f.get("cell") == user["cell"] or f.get("shared"))
            and (cur_folder == "all" or f.get("folder") == cur_folder)
            and (not query or query.lower() in f["name"].lower())
        ]

        if not visible:
            st.info("📂 파일이 없습니다. 업로드하거나 드래그하세요.")
        else:
            for f in visible:
                ext  = f["name"].rsplit(".", 1)[-1].lower() if "." in f["name"] else ""
                ico  = ICONS.get(ext, "📎")
                shared_tag = "🌐" if f.get("shared") else ""
                cell_name = units.get(f.get("cell",""), {}).get("name","")

                c1, c2, c3, c4 = st.columns([3, 1, 1, 1])
                c1.markdown(f"{ico} **{f['name']}** {shared_tag}  \n"
                            f"<small style='color:#9ca3af'>{cell_name} · {f.get('date','')}</small>",
                            unsafe_allow_html=True)
                c2.caption(f.get("size",""))
                if c3.button("↓ 다운", key=f"dl_{f['id']}"):
                    st.toast(f"'{f['name']}' 다운로드 준비 중...")
                if c4.button("🗑", key=f"rm_{f['id']}"):
                    st.session_state.files = [x for x in st.session_state.files if x["id"] != f["id"]]
                    st.rerun()
                st.divider()
