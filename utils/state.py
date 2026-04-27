"""
utils/state.py
Streamlit session_state 초기화 및 공통 데이터 관리
"""
import streamlit as st
from datetime import date, timedelta
import uuid


# ── 기본 유닛/셀 설정 ──────────────────────────────────────
DEFAULT_UNITS = {
    "marketing": {"name": "마케팅",  "emoji": "📣",  "type": "유닛", "color": "#1d4ed8"},
    "analysis":  {"name": "영업분석", "emoji": "📊", "type": "셀",  "color": "#059669"},
    "online":    {"name": "온라인",  "emoji": "💻",  "type": "셀",  "color": "#7c3aed"},
    "md":        {"name": "MD",     "emoji": "🏷️",  "type": "셀",  "color": "#b45309"},
}

DEFAULT_CFG = {
    "manager_pw":  "0000",
    "branch_name": "인천점",
    "team_name":   "영업기획팀",
    "units":       DEFAULT_UNITS,
}

KR_HOLIDAYS = {
    "2026-01-01": "신정",
    "2026-02-16": "설날연휴", "2026-02-17": "설날", "2026-02-18": "설날연휴",
    "2026-03-01": "삼일절",   "2026-03-02": "대체공휴일",
    "2026-05-01": "근로자의 날", "2026-05-05": "어린이날", "2026-05-25": "대체공휴일",
    "2026-06-06": "현충일",
    "2026-07-18": "제헌절",
    "2026-08-15": "광복절",   "2026-08-17": "대체공휴일",
    "2026-09-24": "추석연휴", "2026-09-25": "추석",     "2026-09-26": "추석연휴",
    "2026-10-03": "개천절",   "2026-10-05": "대체공휴일", "2026-10-09": "한글날",
    "2026-11-19": "수능",
    "2026-12-25": "크리스마스",
}

STATUS_LIST = [
    {"key": "todo",   "label": "대기",    "color": "#9ca3af"},
    {"key": "inprog", "label": "진행 중", "color": "#2563eb"},
    {"key": "done",   "label": "완료",    "color": "#059669"},
    {"key": "hold",   "label": "보류",    "color": "#d97706"},
]

EV_TYPES = {
    "promo":    "프로모션",
    "deadline": "마감",
    "meeting":  "회의",
    "etc":      "기타",
}


def today_str(offset: int = 0) -> str:
    return (date.today() + timedelta(days=offset)).isoformat()


def new_id() -> str:
    return str(uuid.uuid4())[:8]


def seed_tasks():
    return [
        {"id": new_id(), "title": "6월 여름 프로모션 기획서 작성", "cell": "marketing",
         "pri": "H", "assignee": "김민준", "due": today_str(2),  "status": "inprog", "desc": "", "shared": False},
        {"id": new_id(), "title": "카카오톡 발송 리스트 정제",     "cell": "marketing",
         "pri": "M", "assignee": "윤지수", "due": today_str(4),  "status": "inprog", "desc": "", "shared": False},
        {"id": new_id(), "title": "2F 리뉴얼 CRM 효과 분석",     "cell": "analysis",
         "pri": "H", "assignee": "박지호", "due": today_str(3),  "status": "inprog", "desc": "", "shared": True},
        {"id": new_id(), "title": "3F 월간 매출 현황 보고서",     "cell": "analysis",
         "pri": "H", "assignee": "이수민", "due": today_str(0),  "status": "inprog", "desc": "", "shared": False},
        {"id": new_id(), "title": "앱 푸시 A/B 테스트 설계",     "cell": "online",
         "pri": "M", "assignee": "정도현", "due": today_str(5),  "status": "todo",   "desc": "", "shared": False},
        {"id": new_id(), "title": "신규 브랜드 입점 협의",        "cell": "md",
         "pri": "H", "assignee": "오재원", "due": today_str(1),  "status": "inprog", "desc": "", "shared": True},
        {"id": new_id(), "title": "MD 행사 상품 리스트 작성",     "cell": "md",
         "pri": "M", "assignee": "강지원", "due": today_str(9),  "status": "todo",   "desc": "", "shared": False},
    ]


def seed_events():
    return [
        {"id": new_id(), "title": "6월 정기 영업회의",    "date": today_str(3),
         "type": "meeting",  "note": "전 셀 참석", "shared": True,  "cell": None, "source": "manual"},
        {"id": new_id(), "title": "여름 프로모션 런칭",   "date": today_str(7),
         "type": "promo",    "note": "전층 동시",  "shared": True,  "cell": None, "source": "manual"},
        {"id": new_id(), "title": "2F CRM 분석 보고",    "date": today_str(5),
         "type": "deadline", "note": "팀장 보고",  "shared": False, "cell": "analysis", "source": "manual"},
    ]


def seed_memos():
    return [
        {"id": new_id(), "title": "6월 전략회의 회의록",
         "content": "참석: 팀장, 각 유닛·셀장\n\n- 여름 프로모션 일정 확정 필요\n- CRM 분석 결과 이번주 금요일까지 공유\n- 온라인 배너 교체 예정",
         "date": today_str(0), "cell": "marketing", "shared": True},
        {"id": new_id(), "title": "MD 신규 브랜드 검토",
         "content": "검토 브랜드: A, B브랜드\n위치: 2F 명품관\n예상 기여: 월 +8%",
         "date": today_str(-1), "cell": "md", "shared": False},
    ]


def init_state():
    """Streamlit session_state 전체 초기화"""
    if "initialized" not in st.session_state:
        st.session_state.initialized   = True
        st.session_state.logged_in     = False
        st.session_state.user          = None
        st.session_state.cfg           = dict(DEFAULT_CFG)
        st.session_state.tasks         = seed_tasks()
        st.session_state.events        = seed_events()
        st.session_state.memos         = seed_memos()
        st.session_state.files         = []
        st.session_state.current_page  = "dashboard"


# ── 접근 제어 ───────────────────────────────────────────────
def can_see_task(task: dict) -> bool:
    user = st.session_state.user
    if not user:
        return False
    if user["cell"] == "manager":
        return True
    return task["cell"] == user["cell"] or task.get("shared", False)


def can_see_event(event: dict) -> bool:
    user = st.session_state.user
    if not user:
        return False
    if user["cell"] == "manager":
        return True
    return event.get("shared", False) or event.get("cell") == user["cell"] or not event.get("cell")


def can_see_memo(memo: dict) -> bool:
    user = st.session_state.user
    if not user:
        return False
    if user["cell"] == "manager":
        return True
    return memo.get("cell") == user["cell"] or memo.get("shared", False)


def get_visible_tasks():
    return [t for t in st.session_state.tasks if can_see_task(t)]


def get_visible_events():
    return [e for e in st.session_state.events if can_see_event(e)]


def get_visible_memos():
    return [m for m in st.session_state.memos if can_see_memo(m)]


# ── Task 캘린더 자동 동기화 ──────────────────────────────────
def sync_tasks_to_calendar():
    """Task 마감일 → events에 자동 등록 (source='task')"""
    st.session_state.events = [
        e for e in st.session_state.events if e.get("source") != "task"
    ]
    for t in st.session_state.tasks:
        if t.get("due") and t.get("status") != "done":
            st.session_state.events.append({
                "id":     f"task_{t['id']}",
                "taskId": t["id"],
                "title":  f"[Task] {t['title']}",
                "date":   t["due"],
                "type":   "task",
                "note":   f"담당: {t.get('assignee','미정')}",
                "shared": t.get("shared", False),
                "cell":   t["cell"],
                "source": "task",
            })
