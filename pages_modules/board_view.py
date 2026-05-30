"""
pages_modules/board_view.py
팀별 익명게시판 & 부문 건의 게시판
"""
import streamlit as st
from datetime import datetime
import uuid

ANIMALS = [
    ("🦊", "여우"), ("🐻", "곰"), ("🐯", "호랑이"), ("🦁", "사자"),
    ("🐺", "늑대"), ("🦝", "너구리"), ("🐨", "코알라"), ("🐼", "판다"),
    ("🦦", "수달"), ("🦔", "고슴도치"), ("🐸", "개구리"), ("🐧", "펭귄"),
    ("🦉", "부엉이"), ("🦚", "공작"), ("🦜", "앵무새"), ("🐬", "돌고래"),
    ("🦋", "나비"), ("🐙", "문어"), ("🦭", "물개"), ("🐘", "코끼리"),
    ("🦒", "기린"), ("🦓", "얼룩말"), ("🦛", "하마"), ("🐪", "낙타"),
    ("🦅", "독수리"), ("🦩", "홍학"), ("🦌", "사슴"), ("🐿️", "다람쥐"),
    ("🦨", "스컹크"), ("🐇", "토끼"),
]


def _now_str() -> str:
    return datetime.now().strftime("%m.%d %H:%M")


def _new_id() -> str:
    return str(uuid.uuid4())[:8]


def _get_my_animal(key: str = "board_animal") -> tuple[str, str]:
    """세션별 랜덤 동물 할당 (새로고침해도 유지)"""
    if key not in st.session_state:
        import random
        emoji, name = random.choice(ANIMALS)
        st.session_state[key] = (emoji, name)
    return st.session_state[key]


def _render_reply_form(post: dict, posts_list: list, save_fn):
    """댓글 입력 폼"""
    my_emoji, my_name = _get_my_animal()
    reply_key = f"reply_input_{post['id']}"
    reply_text = st.text_area(
        "댓글 작성",
        placeholder=f"{my_emoji} {my_name} (으)로 익명 댓글 작성...",
        key=reply_key,
        max_chars=300,
        label_visibility="collapsed",
        height=70,
    )
    if st.button("댓글 등록", key=f"reply_btn_{post['id']}", type="primary"):
        if reply_text.strip():
            if "replies" not in post:
                post["replies"] = []
            post["replies"].append({
                "id":      _new_id(),
                "emoji":   my_emoji,
                "animal":  my_name,
                "content": reply_text.strip(),
                "date":    _now_str(),
            })
            save_fn()
            st.rerun()
        else:
            st.warning("댓글 내용을 입력해주세요.")


def _render_post_card(post: dict, posts_list: list, save_fn, is_manager: bool = False):
    """게시글 카드 렌더링"""
    sid = st.session_state.get("board_session_id", "")
    liked = sid and sid in post.get("liked_sessions", [])
    like_count = len(post.get("liked_sessions", []))
    replies = post.get("replies", [])

    st.markdown(f"""
    <div style="background:white;border:1px solid #e5e7eb;border-radius:12px;
                padding:16px 18px;margin-bottom:2px">
      <div style="display:flex;align-items:center;gap:8px;margin-bottom:10px">
        <span style="font-size:20px">{post['emoji']}</span>
        <span style="font-weight:600;font-size:13px;color:#374151">{post['animal']}</span>
        <span style="font-size:11px;color:#9ca3af;margin-left:auto">{post['date']}</span>
      </div>
      <div style="font-size:14px;color:#111827;line-height:1.7;white-space:pre-wrap">{post['content']}</div>
    </div>
    """, unsafe_allow_html=True)

    btn_cols = st.columns([1, 1, 6] if is_manager else [1, 7])

    with btn_cols[0]:
        like_label = f"{'❤️' if liked else '🤍'} {like_count}"
        if st.button(like_label, key=f"like_{post['id']}", use_container_width=True):
            if not sid:
                st.warning("좋아요를 누르려면 새로고침 후 다시 시도해주세요.")
            elif liked:
                post["liked_sessions"].remove(sid)
                save_fn()
                st.rerun()
            else:
                if "liked_sessions" not in post:
                    post["liked_sessions"] = []
                post["liked_sessions"].append(sid)
                save_fn()
                st.rerun()

    if is_manager:
        with btn_cols[1]:
            if st.button("🗑️ 삭제", key=f"del_{post['id']}", use_container_width=True):
                posts_list[:] = [p for p in posts_list if p["id"] != post["id"]]
                save_fn()
                st.rerun()

    # 댓글
    with st.expander(f"💬 댓글 {len(replies)}개"):
        for r in replies:
            st.markdown(f"""
            <div style="background:#f8fafc;border-left:3px solid #dbeafe;
                        border-radius:6px;padding:8px 12px;margin-bottom:6px">
              <span style="font-size:13px">{r['emoji']}</span>
              <span style="font-weight:600;font-size:12px;color:#374151"> {r['animal']}</span>
              <span style="font-size:11px;color:#9ca3af"> · {r['date']}</span>
              <div style="font-size:13px;color:#374151;margin-top:4px">{r['content']}</div>
            </div>
            """, unsafe_allow_html=True)
        st.divider()
        _render_reply_form(post, posts_list, save_fn)


def render():
    """팀별 익명 게시판"""
    cfg = st.session_state.cfg
    team_name = cfg.get("team_name", "팀")
    is_manager = st.session_state.user.get("cell") == "manager"

    # 메뉴 가시성 체크
    menu_vis = cfg.get("menu_visibility", {})
    if not menu_vis.get("board", True) and not is_manager:
        st.info("현재 게시판이 비공개 상태입니다. 팀장이 활성화하면 이용할 수 있습니다.")
        return

    # session_id 초기화
    if "board_session_id" not in st.session_state:
        st.session_state.board_session_id = str(uuid.uuid4())

    # 팀 게시판 posts 초기화
    tid = st.session_state.get("current_team_id", "")
    td = st.session_state.teams_data.get(tid, {})
    if "board_posts" not in td:
        td["board_posts"] = []
        st.session_state.teams_data[tid] = td

    posts = td["board_posts"]

    def save_posts():
        st.session_state.teams_data[tid]["board_posts"] = posts

    st.markdown(f"### 📌 {team_name} 팀 익명게시판")
    st.caption("모든 작성자는 익명으로 표시됩니다. 서로를 존중하는 글을 써주세요.")

    my_emoji, my_name = _get_my_animal()

    # 글쓰기
    with st.expander("✏️ 글쓰기", expanded=False):
        st.markdown(
            f"<div style='font-size:12px;color:#6b7280;margin-bottom:6px'>"
            f"익명 작성자: {my_emoji} <b>{my_name}</b></div>",
            unsafe_allow_html=True,
        )
        new_content = st.text_area(
            "내용",
            placeholder="자유롭게 의견을 남겨주세요...",
            key="board_new_post",
            max_chars=1000,
            height=120,
            label_visibility="collapsed",
        )
        if st.button("게시하기", type="primary", use_container_width=True, key="board_submit"):
            if new_content.strip():
                posts.insert(0, {
                    "id":             _new_id(),
                    "emoji":          my_emoji,
                    "animal":         my_name,
                    "content":        new_content.strip(),
                    "date":           _now_str(),
                    "likes":          0,
                    "liked_sessions": [],
                    "replies":        [],
                })
                save_posts()
                st.rerun()
            else:
                st.warning("내용을 입력해주세요.")

    st.divider()

    if not posts:
        st.markdown(
            "<div style='text-align:center;color:#9ca3af;padding:40px 0;font-size:14px'>"
            "아직 게시글이 없습니다. 첫 번째로 글을 남겨보세요! 🌱</div>",
            unsafe_allow_html=True,
        )
        return

    for post in posts:
        _render_post_card(post, posts, save_posts, is_manager=is_manager)


def render_branch_board():
    """부문 건의 게시판 (지점 전체 공유)"""
    # session_id 초기화
    if "board_session_id" not in st.session_state:
        st.session_state.board_session_id = str(uuid.uuid4())

    is_manager = st.session_state.user.get("cell") in ("manager", "store_manager")

    # branch_board_posts 초기화
    if "branch_board_posts" not in st.session_state:
        st.session_state.branch_board_posts = []

    posts = st.session_state.branch_board_posts

    def save_posts():
        st.session_state.branch_board_posts = posts

    branch_name = st.session_state.branch_cfg.get("branch_name", "인천점")
    st.markdown(f"### 💬 {branch_name} 부문 건의 게시판")
    st.caption("팀 구분 없이 부문 전체에 건의사항을 익명으로 남길 수 있습니다.")

    my_emoji, my_name = _get_my_animal(key="branch_board_animal")

    with st.expander("✏️ 건의사항 작성", expanded=False):
        st.markdown(
            f"<div style='font-size:12px;color:#6b7280;margin-bottom:6px'>"
            f"익명 작성자: {my_emoji} <b>{my_name}</b></div>",
            unsafe_allow_html=True,
        )
        new_content = st.text_area(
            "건의 내용",
            placeholder="부문에 건의하고 싶은 내용을 자유롭게 적어주세요...",
            key="branch_board_new_post",
            max_chars=1000,
            height=120,
            label_visibility="collapsed",
        )
        if st.button("건의하기", type="primary", use_container_width=True, key="branch_board_submit"):
            if new_content.strip():
                posts.insert(0, {
                    "id":             _new_id(),
                    "emoji":          my_emoji,
                    "animal":         my_name,
                    "content":        new_content.strip(),
                    "date":           _now_str(),
                    "likes":          0,
                    "liked_sessions": [],
                    "replies":        [],
                })
                save_posts()
                st.rerun()
            else:
                st.warning("내용을 입력해주세요.")

    st.divider()

    if not posts:
        st.markdown(
            "<div style='text-align:center;color:#9ca3af;padding:40px 0;font-size:14px'>"
            "아직 건의사항이 없습니다. 첫 번째로 건의해보세요! 💡</div>",
            unsafe_allow_html=True,
        )
        return

    for post in posts:
        _render_post_card(post, posts, save_posts, is_manager=is_manager)
