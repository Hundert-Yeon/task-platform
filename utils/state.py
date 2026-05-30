"""
utils/state.py
Streamlit session_state 초기화 및 공통 데이터 관리
"""
import streamlit as st
from datetime import date, timedelta
import uuid


# ── 유닛 타입 옵션 ────────────────────────────────────────────────
TYPE_OPTIONS = ["팀", "유닛", "셀", "파트"]

# ── 기본 유닛/셀 설정 (영업기획팀) ───────────────────────────────
DEFAULT_UNITS = {
    "marketing": {"name": "마케팅",   "emoji": "📣",  "type": "유닛", "color": "#1d4ed8"},
    "analysis":  {"name": "영업분석", "emoji": "📊",  "type": "셀",  "color": "#059669"},
    "online":    {"name": "온라인",   "emoji": "💻",  "type": "셀",  "color": "#7c3aed"},
    "md":        {"name": "MD",      "emoji": "🏷️", "type": "셀",  "color": "#b45309"},
}

# ── 기본 파트 설정 (지원팀) ──────────────────────────────────────
DEFAULT_SUPPORT_UNITS = {
    "hr_part":      {"name": "인사파트", "emoji": "👥", "type": "파트", "color": "#dc2626"},
    "support_part": {"name": "지원파트", "emoji": "🛠️", "type": "파트", "color": "#7c3aed"},
}

DEFAULT_MENU_VISIBILITY = {
    "dashboard":   True,
    "tasks":       True,
    "calendar":    True,
    "files":       True,
    "memo":        True,
    "shared_feed": True,
    "board":       True,
}

# ── 지점 전역 설정 ────────────────────────────────────────────────
DEFAULT_BRANCH_CFG = {
    "branch_name":          "인천점",
    "store_manager_pw":     "0000",
    "global_files_enabled": True,
}

# ── 팀 정의 ──────────────────────────────────────────────────────
DEFAULT_TEAMS = {
    "sales_planning": {
        "team_name":       "영업기획팀",
        "manager_pw":      "0000",
        "units":           DEFAULT_UNITS,
        "menu_visibility": dict(DEFAULT_MENU_VISIBILITY),
    },
    "support": {
        "team_name":       "지원팀",
        "manager_pw":      "0000",
        "units":           DEFAULT_SUPPORT_UNITS,
        "menu_visibility": dict(DEFAULT_MENU_VISIBILITY),
    },
}

# ── (하위 호환) ───────────────────────────────────────────────────
DEFAULT_CFG = {
    "manager_pw":      "0000",
    "branch_name":     "인천점",
    "team_name":       "영업기획팀",
    "units":           DEFAULT_UNITS,
    "menu_visibility": dict(DEFAULT_MENU_VISIBILITY),
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
         "pri": "H", "assignee": "김민준", "due": today_str(2),  "status": "inprog",
         "desc": "", "shared": False, "shared_branch": False},
        {"id": new_id(), "title": "카카오톡 발송 리스트 정제",     "cell": "marketing",
         "pri": "M", "assignee": "윤지수", "due": today_str(4),  "status": "inprog",
         "desc": "", "shared": False, "shared_branch": False},
        {"id": new_id(), "title": "2F 리뉴얼 CRM 효과 분석",     "cell": "analysis",
         "pri": "H", "assignee": "박지호", "due": today_str(3),  "status": "inprog",
         "desc": "", "shared": True,  "shared_branch": False},
        {"id": new_id(), "title": "3F 월간 매출 현황 보고서",     "cell": "analysis",
         "pri": "H", "assignee": "이수민", "due": today_str(0),  "status": "inprog",
         "desc": "", "shared": False, "shared_branch": False},
        {"id": new_id(), "title": "앱 푸시 A/B 테스트 설계",     "cell": "online",
         "pri": "M", "assignee": "정도현", "due": today_str(5),  "status": "todo",
         "desc": "", "shared": False, "shared_branch": False},
        {"id": new_id(), "title": "신규 브랜드 입점 협의",        "cell": "md",
         "pri": "H", "assignee": "오재원", "due": today_str(1),  "status": "inprog",
         "desc": "", "shared": True,  "shared_branch": False},
        {"id": new_id(), "title": "MD 행사 상품 리스트 작성",     "cell": "md",
         "pri": "M", "assignee": "강지원", "due": today_str(9),  "status": "todo",
         "desc": "", "shared": False, "shared_branch": False},
    ]


def seed_tasks_support():
    return [
        {"id": new_id(), "title": "신규 직원 채용 공고 작성",   "cell": "hr_part",
         "pri": "H", "assignee": "이인사", "due": today_str(3),  "status": "inprog",
         "desc": "", "shared": False, "shared_branch": False},
        {"id": new_id(), "title": "복리후생 제도 개선안 검토",   "cell": "hr_part",
         "pri": "M", "assignee": "김복지", "due": today_str(7),  "status": "todo",
         "desc": "", "shared": False, "shared_branch": False},
        {"id": new_id(), "title": "사무용품 재고 확인 및 발주", "cell": "support_part",
         "pri": "M", "assignee": "박지원", "due": today_str(2),  "status": "inprog",
         "desc": "", "shared": False, "shared_branch": False},
        {"id": new_id(), "title": "매장 청소 업체 계약 갱신",   "cell": "support_part",
         "pri": "H", "assignee": "최관리", "due": today_str(5),  "status": "todo",
         "desc": "", "shared": True,  "shared_branch": False},
    ]


def seed_events():
    return [
        {"id": new_id(), "title": "6월 정기 영업회의",    "date": today_str(3),
         "type": "meeting",  "note": "전 셀 참석", "shared": True,  "shared_branch": False,
         "cell": None, "source": "manual"},
        {"id": new_id(), "title": "여름 프로모션 런칭",   "date": today_str(7),
         "type": "promo",    "note": "전층 동시",  "shared": True,  "shared_branch": False,
         "cell": None, "source": "manual"},
        {"id": new_id(), "title": "2F CRM 분석 보고",    "date": today_str(5),
         "type": "deadline", "note": "팀장 보고",  "shared": False, "shared_branch": False,
         "cell": "analysis", "source": "manual"},
    ]


def seed_events_support():
    return [
        {"id": new_id(), "title": "월례 직원 회의", "date": today_str(5),
         "type": "meeting", "note": "전 직원 참석", "shared": True, "shared_branch": False,
         "cell": None, "source": "manual"},
    ]


def seed_memos():
    return [
        {"id": new_id(), "title": "6월 전략회의 회의록",
         "content": "참석: 팀장, 각 유닛·셀장\n\n- 여름 프로모션 일정 확정 필요\n- CRM 분석 결과 이번주 금요일까지 공유\n- 온라인 배너 교체 예정",
         "date": today_str(0), "cell": "marketing", "shared": True, "shared_branch": False},
        {"id": new_id(), "title": "MD 신규 브랜드 검토",
         "content": "검토 브랜드: A, B브랜드\n위치: 2F 명품관\n예상 기여: 월 +8%",
         "date": today_str(-1), "cell": "md", "shared": False, "shared_branch": False},
    ]


def seed_memos_support():
    return [
        {"id": new_id(), "title": "6월 채용 계획",
         "content": "- 영업직 3명 신규 채용 예정\n- 면접: 6월 중순\n- 합격자 발표: 6월 말",
         "date": today_str(0), "cell": "hr_part", "shared": False, "shared_branch": False},
    ]


def _build_team_cfg(team_def: dict, branch_name: str) -> dict:
    return {
        "manager_pw":      team_def["manager_pw"],
        "team_name":       team_def["team_name"],
        "branch_name":     branch_name,
        "units":           {k: dict(v) for k, v in team_def["units"].items()},
        "menu_visibility": dict(team_def.get("menu_visibility", DEFAULT_MENU_VISIBILITY)),
    }


def _load_team(team_id: str):
    """팀 데이터를 활성 세션 변수로 로드"""
    td = st.session_state.teams_data[team_id]
    st.session_state.cfg    = td["cfg"]
    st.session_state.tasks  = td["tasks"]
    st.session_state.events = td["events"]
    st.session_state.memos  = td["memos"]
    st.session_state.files  = td["files"]
    st.session_state.current_team_id = team_id


def save_current_team():
    """활성 세션 변수를 teams_data에 저장"""
    tid = st.session_state.get("current_team_id")
    if not tid or "teams_data" not in st.session_state:
        return
    st.session_state.teams_data[tid] = {
        "cfg":    st.session_state.cfg,
        "tasks":  st.session_state.tasks,
        "events": st.session_state.events,
        "memos":  st.session_state.memos,
        "files":  st.session_state.files,
    }


def switch_team(team_id: str):
    """현재 팀 저장 후 새 팀으로 전환"""
    save_current_team()
    _load_team(team_id)


def get_all_teams() -> list[tuple[str, str]]:
    """(team_id, team_name) 목록 반환"""
    teams_data = st.session_state.get("teams_data", {})
    return [(tid, td["cfg"]["team_name"]) for tid, td in teams_data.items()]


def init_state():
    """Streamlit session_state 전체 초기화"""
    if "initialized" not in st.session_state:
        st.session_state.initialized  = True
        st.session_state.logged_in    = False
        st.session_state.user         = None
        st.session_state.current_page = "dashboard"
        st.session_state.branch_cfg   = dict(DEFAULT_BRANCH_CFG)

        branch_name = DEFAULT_BRANCH_CFG["branch_name"]
        st.session_state.teams_data = {
            "sales_planning": {
                "cfg":    _build_team_cfg(DEFAULT_TEAMS["sales_planning"], branch_name),
                "tasks":  seed_tasks(),
                "events": seed_events(),
                "memos":  seed_memos(),
                "files":  [],
            },
            "support": {
                "cfg":    _build_team_cfg(DEFAULT_TEAMS["support"], branch_name),
                "tasks":  seed_tasks_support(),
                "events": seed_events_support(),
                "memos":  seed_memos_support(),
                "files":  [],
            },
        }

        # 기본 활성 팀: 영업기획팀
        _load_team("sales_planning")


# ── 접근 제어 ───────────────────────────────────────────────
def _is_admin_user() -> bool:
    user = st.session_state.get("user")
    return user and user.get("cell") in ("manager", "store_manager")


def can_see_task(task: dict) -> bool:
    user = st.session_state.user
    if not user:
        return False
    if user["cell"] in ("manager", "store_manager"):
        return True
    return task["cell"] == user["cell"] or task.get("shared", False) or task.get("shared_branch", False)


def can_see_event(event: dict) -> bool:
    user = st.session_state.user
    if not user:
        return False
    if user["cell"] in ("manager", "store_manager"):
        return True
    return (event.get("shared", False) or event.get("shared_branch", False)
            or event.get("cell") == user["cell"] or not event.get("cell"))


def can_see_memo(memo: dict) -> bool:
    user = st.session_state.user
    if not user:
        return False
    if user["cell"] in ("manager", "store_manager"):
        return True
    return (memo.get("cell") == user["cell"]
            or memo.get("shared", False) or memo.get("shared_branch", False))


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
                "id":            f"task_{t['id']}",
                "taskId":        t["id"],
                "title":         f"[Task] {t['title']}",
                "date":          t["due"],
                "type":          "task",
                "note":          f"담당: {t.get('assignee','미정')}",
                "shared":        t.get("shared", False),
                "shared_branch": t.get("shared_branch", False),
                "cell":          t["cell"],
                "source":        "task",
            })
