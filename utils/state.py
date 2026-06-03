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

# ── 남성스포츠팀 ──────────────────────────────────────────────────
DEFAULT_MENS_SPORTS_UNITS = {
    "sports_gear":  {"name": "스포츠용품", "emoji": "🏃", "type": "유닛", "color": "#0369a1"},
    "golf":         {"name": "골프",       "emoji": "⛳", "type": "셀",  "color": "#166534"},
    "outdoor":      {"name": "아웃도어",   "emoji": "🏕️", "type": "셀",  "color": "#9a3412"},
    "mens_fashion": {"name": "남성패션",   "emoji": "👔", "type": "셀",  "color": "#1e1b4b"},
}

# ── 여성팀 ───────────────────────────────────────────────────────
DEFAULT_WOMENS_UNITS = {
    "womens_fashion": {"name": "여성패션", "emoji": "👗", "type": "유닛", "color": "#9d174d"},
    "beauty":         {"name": "뷰티",     "emoji": "💄", "type": "셀",  "color": "#be123c"},
    "accessories":    {"name": "잡화",     "emoji": "👜", "type": "셀",  "color": "#7e22ce"},
    "lingerie":       {"name": "란제리",   "emoji": "🌸", "type": "셀",  "color": "#db2777"},
}

# ── 생활가전팀 ───────────────────────────────────────────────────
DEFAULT_LIVING_UNITS = {
    "appliances": {"name": "가전제품",     "emoji": "📺", "type": "유닛", "color": "#0f766e"},
    "living":     {"name": "생활용품",     "emoji": "🏠", "type": "셀",  "color": "#047857"},
    "kitchen":    {"name": "주방용품",     "emoji": "🍳", "type": "셀",  "color": "#b45309"},
    "furniture":  {"name": "가구/인테리어","emoji": "🪑", "type": "셀",  "color": "#92400e"},
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
    "mens_sports": {
        "team_name":       "남성스포츠팀",
        "manager_pw":      "0000",
        "units":           DEFAULT_MENS_SPORTS_UNITS,
        "menu_visibility": dict(DEFAULT_MENU_VISIBILITY),
    },
    "womens": {
        "team_name":       "여성팀",
        "manager_pw":      "0000",
        "units":           DEFAULT_WOMENS_UNITS,
        "menu_visibility": dict(DEFAULT_MENU_VISIBILITY),
    },
    "living": {
        "team_name":       "생활가전팀",
        "manager_pw":      "0000",
        "units":           DEFAULT_LIVING_UNITS,
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
    def t(title, cell, pri, assignee, due_offset, status, shared=False):
        return {"id": new_id(), "title": title, "cell": cell, "pri": pri,
                "assignee": assignee, "due": today_str(due_offset),
                "status": status, "desc": "", "shared": shared, "shared_branch": False}

    return [
        # ── 마케팅 (10) ──────────────────────────────────────────
        t("6월 여름 프로모션 기획서 작성",        "marketing", "H", "김민준",   2,   "inprog", True),
        t("카카오톡 발송 리스트 정제",            "marketing", "M", "윤지수",   4,   "inprog"),
        t("SNS 인스타그램 여름 컨텐츠 기획",      "marketing", "M", "박소영",   8,   "todo"),
        t("7월 VIP 고객 초청 행사 준비",          "marketing", "H", "이현우",   14,  "todo"),
        t("여름 배너 디자인 시안 검토",            "marketing", "M", "정예린",   3,   "inprog"),
        t("5월 프로모션 결과 보고서 작성",         "marketing", "M", "김민준",  -5,   "done"),
        t("신규 회원 온보딩 이메일 발송",          "marketing", "L", "윤지수", -10,   "done"),
        t("8월 추석 프로모션 사전 기획",           "marketing", "H", "박소영",  45,   "todo"),
        t("브랜드 협업 마케팅 제안서 작성",        "marketing", "M", "이현우",  20,   "todo"),
        t("월간 마케팅 성과 보고 자료 준비",       "marketing", "M", "정예린",   6,   "inprog"),

        # ── 영업분석 (10) ────────────────────────────────────────
        t("2F 리뉴얼 CRM 효과 분석",            "analysis",  "H", "박지호",   3,   "inprog", True),
        t("3F 월간 매출 현황 보고서",            "analysis",  "H", "이수민",   0,   "inprog"),
        t("1분기 층별 매출 종합 분석",           "analysis",  "H", "최재원", -30,   "done",   True),
        t("VIP 고객 이탈률 원인 분석",           "analysis",  "H", "한지민",   5,   "inprog"),
        t("5월 KPI 대시보드 업데이트",           "analysis",  "M", "오동현",  -2,   "done"),
        t("층별 임대 수익성 비교 분석",           "analysis",  "M", "박지호",  15,   "todo"),
        t("신규 입점 브랜드 매출 기여도 분석",   "analysis",  "H", "이수민",   4,   "inprog"),
        t("고객 재방문율 3개월 추이 분석",        "analysis",  "M", "최재원",  10,   "todo"),
        t("6월 프로모션 ROI 사전 추정",          "analysis",  "H", "한지민",   1,   "todo"),
        t("경쟁 백화점 벤치마킹 조사",           "analysis",  "M", "오동현", -20,   "done"),

        # ── 온라인 (10) ──────────────────────────────────────────
        t("앱 푸시 A/B 테스트 설계",            "online",    "M", "정도현",   5,   "todo"),
        t("온라인몰 여름 시즌 UI 개편 검토",     "online",    "H", "강하늘",  10,   "inprog"),
        t("모바일 앱 6월 업데이트 QA 테스트",   "online",    "M", "서지원",   3,   "inprog"),
        t("온라인 전용 여름 할인 이벤트 기획",   "online",    "H", "임채은",   7,   "todo"),
        t("상품 상세페이지 SEO 최적화 작업",     "online",    "L", "유태양", -15,   "done"),
        t("신상품 이미지 업로드 및 등록",         "online",    "M", "정도현",   2,   "inprog"),
        t("온라인 고객 리뷰 모니터링 및 대응",   "online",    "L", "강하늘",  -5,   "done"),
        t("앱 이용자 행동 데이터 분석",          "online",    "M", "서지원",  12,   "todo"),
        t("퀵배송 서비스 운영 프로세스 개선",    "online",    "H", "임채은",   8,   "inprog"),
        t("6월 온라인 전용 쿠폰 발급 기획",      "online",    "M", "유태양",  -3,   "done"),

        # ── MD (10) ─────────────────────────────────────────────
        t("신규 브랜드 입점 협의",               "md",        "H", "오재원",   1,   "inprog", True),
        t("MD 행사 상품 리스트 작성",            "md",        "M", "강지원",   9,   "todo"),
        t("입점 브랜드 5월 매출 정산 확인",       "md",        "H", "신민서",  -5,   "done"),
        t("A브랜드 계약 갱신 협상",              "md",        "H", "류준혁",  15,   "inprog"),
        t("식품관 신규 카테고리 입점 검토",       "md",        "M", "백서연",  20,   "todo"),
        t("해외 명품 브랜드 수입 타당성 검토",    "md",        "H", "오재원",  35,   "todo"),
        t("3F 매장 레이아웃 변경 기획",           "md",        "M", "강지원",  12,   "inprog"),
        t("F/W 시즌 상품 구성 기획",             "md",        "H", "신민서",  50,   "todo"),
        t("입점 브랜드 6월 VMD 지도",            "md",        "M", "류준혁",   5,   "inprog"),
        t("여름 기획 행사 공간 배치 계획",        "md",        "M", "백서연",  -3,   "done"),
    ]


def seed_tasks_support():
    def t(title, cell, pri, assignee, due_offset, status, shared=False):
        return {"id": new_id(), "title": title, "cell": cell, "pri": pri,
                "assignee": assignee, "due": today_str(due_offset),
                "status": status, "desc": "", "shared": shared, "shared_branch": False}

    return [
        # ── 인사파트 (10) ────────────────────────────────────────
        t("신규 직원 채용 공고 작성",            "hr_part", "H", "이인사",   3,   "inprog"),
        t("복리후생 제도 개선안 검토",            "hr_part", "M", "김복지",   7,   "todo"),
        t("신입 직원 온보딩 프로그램 준비",       "hr_part", "M", "장채원",   5,   "inprog"),
        t("직원 만족도 설문 진행 및 분석",        "hr_part", "M", "송인국", -15,   "done",  True),
        t("6월 급여 대장 정리 및 확인",           "hr_part", "H", "민지혜",   1,   "inprog"),
        t("5월 연차 사용 현황 집계 보고",         "hr_part", "L", "이인사", -10,   "done"),
        t("하반기 직무 교육 일정 편성",           "hr_part", "M", "김복지",  20,   "todo"),
        t("우수 직원 포상 계획 수립",             "hr_part", "M", "장채원",  25,   "todo"),
        t("퇴직자 업무 인수인계 지원",            "hr_part", "H", "송인국",   4,   "inprog"),
        t("7월 채용 면접 일정 조율",              "hr_part", "H", "민지혜",  15,   "todo"),

        # ── 지원파트 (10) ────────────────────────────────────────
        t("사무용품 재고 확인 및 발주",           "support_part", "M", "박지원",   2,   "inprog"),
        t("매장 청소 업체 계약 갱신",             "support_part", "H", "최관리",   5,   "todo",  True),
        t("6월 시설 정기 점검 체크리스트 작성",   "support_part", "M", "한재형",  -5,   "done"),
        t("냉난방 설비 하절기 점검 예약",         "support_part", "H", "임소연",   3,   "inprog"),
        t("주차 관리 시스템 개선 방안 검토",      "support_part", "M", "조성민",  18,   "todo"),
        t("긴급 소모품 구매 요청 처리",           "support_part", "M", "박지원",  -3,   "done"),
        t("건물 소방 안전 점검 대응",             "support_part", "H", "최관리",   1,   "inprog"),
        t("엘리베이터 정기 검사 일정 조율",       "support_part", "M", "한재형",  12,   "todo"),
        t("매장 LED 조명 교체 공사 협의",         "support_part", "M", "임소연",   9,   "inprog"),
        t("폐기물 처리 업체 계약 갱신 검토",      "support_part", "M", "조성민",  20,   "todo"),
    ]


def seed_events():
    def e(title, offset, typ, note, cell=None, shared=True):
        return {"id": new_id(), "title": title, "date": today_str(offset),
                "type": typ, "note": note, "shared": shared,
                "shared_branch": False, "cell": cell, "source": "manual"}

    return [
        e("6월 정기 영업회의",              3,   "meeting",  "전 셀 참석"),
        e("여름 프로모션 런칭",             7,   "promo",    "전층 동시 진행"),
        e("2F CRM 분석 결과 보고",          5,   "deadline", "팀장 보고",          "analysis", False),
        e("마케팅팀 월간 성과 보고",         6,   "meeting",  "마케팅 전체",        "marketing"),
        e("7월 VIP 고객 초청 행사",         14,  "promo",    "VIP 200명 초청"),
        e("온라인몰 앱 5.0 업데이트 출시",  6,   "promo",    "앱스토어 배포",       "online",  False),
        e("신규 브랜드 입점 협의 미팅",      1,   "meeting",  "C브랜드 담당자",      "md",      False),
        e("5월 월간 매출 보고",            -5,   "deadline", "경영진 보고",         None,       True),
        e("추석 프로모션 기획 착수 회의",   45,  "meeting",  "전 셀 참여"),
        e("2분기 사업 성과 보고회",         30,  "deadline", "경영진 발표"),
        e("라이브커머스 7월 첫 방송",       25,  "promo",    "인플루언서 협업",     "online"),
        e("하반기 사업 계획 수립 회의",     55,  "meeting",  "전체 팀 참여"),
    ]


def seed_events_support():
    def e(title, offset, typ, note, cell=None, shared=True):
        return {"id": new_id(), "title": title, "date": today_str(offset),
                "type": typ, "note": note, "shared": shared,
                "shared_branch": False, "cell": cell, "source": "manual"}

    return [
        e("월례 직원 회의",              5,   "meeting",  "전 직원 참석"),
        e("건물 소방 안전 점검",          1,   "deadline", "소방서 공식 점검",     None,  False),
        e("신입 직원 채용 면접",         15,  "meeting",  "인사파트 주관",        "hr_part", False),
        e("분기 고충 처리 위원회",        30,  "meeting",  "위원 5명 참석"),
        e("시설 정기 점검",               3,  "deadline", "전 구역 점검"),
        e("직원 역량 강화 교육",          22,  "meeting",  "외부 강사 초청"),
        e("5월 급여 지급",               -5,  "deadline", "급여일",              "hr_part", False),
        e("하반기 팀빌딩 워크숍",         45,  "meeting",  "숙박 워크숍"),
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


def seed_board_posts():
    """팀 익명 게시판 더미 데이터"""
    def p(emoji, animal, content, date, replies=None, likes=0):
        return {"id": new_id(), "emoji": emoji, "animal": animal, "content": content,
                "date": date, "likes": likes, "liked_sessions": [], "replies": replies or []}
    def r(emoji, animal, content, date):
        return {"id": new_id(), "emoji": emoji, "animal": animal, "content": content, "date": date}

    return [
        p("🐙", "문어", "업무 시스템에 건의사항인데요, 엑셀 공유 문서 버전 충돌이 너무 자주 생겨요. 구글시트나 공유 폴더 체계 개선이 필요할 것 같습니다.",
          "05.29 09:50", likes=3, replies=[
            r("🦜", "앵무새", "완전 공감이에요. 저도 오늘 덮어쓰기 사고 났어요 ㅠㅠ", "05.29 10:15"),
          ]),
        p("🦊", "여우", "이번 여름 프로모션 정말 기대됩니다! 팀 모두 수고 많으세요 💪 우리 팀 화이팅!",
          "05.28 13:35", likes=7, replies=[
            r("🐻", "곰", "같이 잘 해봐요! 파이팅!", "05.28 14:00"),
          ]),
        p("🐯", "호랑이", "요즘 야근이 너무 많은 것 같아요. 업무 분배가 좀 더 효율적으로 이루어졌으면 좋겠습니다. 솔직히 번아웃 올 것 같아요.",
          "05.27 10:20", likes=5, replies=[
            r("🦦", "수달", "맞아요 저도 같은 생각이에요. 팀장님께 말씀드려보는 건 어떨까요", "05.27 11:00"),
          ]),
        p("🐧", "펭귄", "팀 회식 언제 하나요? 오래됐는데... 다들 바빠서 날 잡기가 어렵죠 ㅎㅎ 한 번 편하게 모이고 싶어요.",
          "05.26 16:45", likes=9, replies=[
            r("🦝", "너구리", "저도 기대하고 있어요! 빨리 날 잡혔으면 좋겠네요", "05.26 17:10"),
          ]),
    ]


def seed_branch_board_posts():
    """부문(점) 건의 게시판 더미 데이터"""
    def p(emoji, animal, content, date, replies=None, likes=0):
        return {"id": new_id(), "emoji": emoji, "animal": animal, "content": content,
                "date": date, "likes": likes, "liked_sessions": [], "replies": replies or []}
    def r(emoji, animal, content, date):
        return {"id": new_id(), "emoji": emoji, "animal": animal, "content": content, "date": date}

    return [
        p("🦒", "기린", "엘리베이터 대기 시간이 너무 길어서 고객 불만이 자주 있습니다. 운행 간격 조정이나 추가 방안이 필요할 것 같아요.",
          "05.29 14:30", likes=8, replies=[
            r("🐪", "낙타", "저도 고객분께 이 얘기 들었어요. 빠른 조치가 필요합니다", "05.29 15:00"),
          ]),
        p("🐙", "문어", "직원 할인 혜택을 조금 더 확대해주시면 좋겠습니다. 근무 만족도에도 영향을 줄 것 같아요.",
          "05.28 16:00", likes=15, replies=[
            r("🦓", "얼룩말", "꼭 반영됐으면 합니다!", "05.28 16:30"),
          ]),
        p("🦭", "물개", "고객 주차 안내 시스템이 좀 더 직관적이었으면 좋겠습니다. 처음 오시는 분들이 많이 헤매시더라고요.",
          "05.27 11:15", likes=6),
        p("🦋", "나비", "1층 고객 화장실 청결 상태가 많이 아쉽습니다. 주말에 특히 관리가 잘 안 되는 것 같아요. 개선해주세요.",
          "05.25 14:00", likes=10, replies=[
            r("🐸", "개구리", "저도 느꼈어요. 빨리 개선되었으면 합니다.", "05.25 14:30"),
          ]),
    ]


def seed_tasks_mens_sports():
    def t(title, cell, pri, assignee, due_offset, status, shared=False):
        return {"id": new_id(), "title": title, "cell": cell, "pri": pri,
                "assignee": assignee, "due": today_str(due_offset),
                "status": status, "desc": "", "shared": shared, "shared_branch": False}
    return [
        # ── 스포츠용품 (10) ──────────────────────────────────────
        t("나이키 여름 신상품 입고 검수",          "sports_gear", "H", "김태준",   2,  "inprog"),
        t("여름 스포츠웨어 플로어 진열 교체",      "sports_gear", "M", "이정호",   8,  "todo"),
        t("아디다스 특가 행사 상품 준비",          "sports_gear", "M", "박민수",   3,  "inprog"),
        t("스포츠용품 6월 재고 조사",             "sports_gear", "M", "최승현",  -5,  "done"),
        t("러닝화 여름 할인 행사 기획",            "sports_gear", "H", "오지은",  10,  "todo"),
        t("나이키·아디다스 계약 갱신 협상",        "sports_gear", "H", "김태준",  15,  "inprog"),
        t("수영용품 시즌 진열 기획",              "sports_gear", "M", "이정호",  -8,  "done"),
        t("사이즈 불량 상품 반품 처리",           "sports_gear", "L", "박민수",  -3,  "done"),
        t("스포츠 액세서리 신규 입점 검토",        "sports_gear", "M", "최승현",  20,  "todo"),
        t("5월 스포츠용품 매출 보고",             "sports_gear", "H", "오지은", -10,  "done",  True),
        # ── 골프 (10) ────────────────────────────────────────────
        t("여름 골프웨어 신상 입고 검수",         "golf", "H", "정재원",   2,  "inprog"),
        t("골프클럽 여름 할인 행사 기획",         "golf", "H", "한승호",  10,  "todo"),
        t("골프용품 VMD 교체",                   "golf", "M", "신지훈",  -5,  "done"),
        t("프리미엄 골프클럽 신규 입점 협의",     "golf", "H", "임태양",  14,  "inprog"),
        t("골프 시뮬레이터 체험 행사 기획",       "golf", "M", "유승우",  20,  "todo"),
        t("골프 액세서리 재고 조사",              "golf", "L", "정재원",  -8,  "done"),
        t("5월 골프 매출 분석 보고",              "golf", "H", "한승호", -10,  "done",  True),
        t("골프웨어 브랜드 계약 갱신",            "golf", "H", "신지훈",   8,  "inprog"),
        t("여름 골프 투어 패키지 협업 기획",      "golf", "M", "임태양",  25,  "todo"),
        t("골프클럽 피팅 서비스 기획",            "golf", "L", "유승우",  30,  "todo"),
        # ── 아웃도어 (10) ────────────────────────────────────────
        t("여름 등산복 신상품 입고 검수",         "outdoor", "H", "강동훈",   3,  "inprog"),
        t("캠핑용품 시즌 진열 기획",             "outdoor", "M", "박재민",   7,  "todo"),
        t("아웃도어 브랜드 계약 갱신",           "outdoor", "H", "이선호",  12,  "inprog"),
        t("등산 장비 재고 조사",                "outdoor", "M", "최민찬",  -5,  "done"),
        t("캠핑 체험 행사 기획서 작성",          "outdoor", "H", "서준영",  15,  "todo"),
        t("트레킹화 여름 특가 행사 기획",        "outdoor", "M", "강동훈",  10,  "todo"),
        t("아웃도어 VMD 여름 업데이트",          "outdoor", "M", "박재민",  -7,  "done"),
        t("신규 캠핑 브랜드 입점 협의",          "outdoor", "H", "이선호",  18,  "inprog"),
        t("등산용품 5월 매출 분석",             "outdoor", "H", "최민찬", -12,  "done",  True),
        t("F/W 아웃도어 소싱 계획",             "outdoor", "H", "서준영",  55,  "todo"),
        # ── 남성패션 (10) ────────────────────────────────────────
        t("여름 남성 수트 신상 입고",            "mens_fashion", "H", "윤성민",   2,  "inprog"),
        t("캐주얼 라인 VMD 여름 교체",           "mens_fashion", "M", "조현우",   6,  "todo"),
        t("남성 브랜드 계약 갱신 협상",          "mens_fashion", "H", "신재원",  14,  "inprog"),
        t("남성 셔츠 여름 특가 행사 기획",       "mens_fashion", "H", "김도훈",   8,  "todo"),
        t("5월 남성 의류 매출 분석",             "mens_fashion", "H", "이승준",  -8,  "done",  True),
        t("신규 남성 편집숍 입점 협의",          "mens_fashion", "M", "윤성민",  20,  "todo"),
        t("남성 정장 재고 현황 파악",            "mens_fashion", "M", "조현우",  -5,  "done"),
        t("F/W 남성 코트 소싱 계획",             "mens_fashion", "H", "신재원",  50,  "todo"),
        t("남성 패션 룩북 촬영 기획",            "mens_fashion", "M", "김도훈",  10,  "inprog"),
        t("제휴 카드 남성 의류 할인 기획",       "mens_fashion", "M", "이승준", -15,  "done"),
    ]


def seed_tasks_womens():
    def t(title, cell, pri, assignee, due_offset, status, shared=False):
        return {"id": new_id(), "title": title, "cell": cell, "pri": pri,
                "assignee": assignee, "due": today_str(due_offset),
                "status": status, "desc": "", "shared": shared, "shared_branch": False}
    return [
        # ── 여성패션 (10) ────────────────────────────────────────
        t("여름 여성 드레스 신상 입고",          "womens_fashion", "H", "박지영",   2,  "inprog"),
        t("여성 의류 플로어 VMD 교체",           "womens_fashion", "M", "이서연",   7,  "todo"),
        t("여성 브랜드 계약 갱신 협상",          "womens_fashion", "H", "김혜진",  15,  "inprog"),
        t("여름 특가 여성복 행사 기획",          "womens_fashion", "H", "최수민",  10,  "todo"),
        t("5월 여성 의류 매출 분석",             "womens_fashion", "H", "정아름",  -8,  "done",  True),
        t("신규 여성 편집숍 입점 협의",          "womens_fashion", "M", "박지영",  22,  "todo"),
        t("여성 정장 재고 파악 및 정리",         "womens_fashion", "M", "이서연",  -5,  "done"),
        t("F/W 여성 컬렉션 소싱 계획",           "womens_fashion", "H", "김혜진",  55,  "todo"),
        t("여성 패션 룩북 촬영 기획",            "womens_fashion", "M", "최수민",  12,  "inprog"),
        t("VIP 여성 스타일링 행사 준비",         "womens_fashion", "H", "정아름",  18,  "todo"),
        # ── 뷰티 (10) ────────────────────────────────────────────
        t("6월 뷰티 신상품 입고 검수",           "beauty", "H", "한소희",   2,  "inprog"),
        t("여름 선케어 특별 기획전 준비",         "beauty", "H", "오지현",   7,  "todo"),
        t("화장품 브랜드 계약 갱신",             "beauty", "H", "강예진",  12,  "inprog"),
        t("뷰티 VMD 여름 시즌 교체",            "beauty", "M", "임수연",  -5,  "done"),
        t("5월 뷰티 매출 분석 보고",            "beauty", "H", "신채원", -10,  "done",  True),
        t("신규 K-뷰티 브랜드 입점 협의",       "beauty", "H", "한소희",  20,  "todo"),
        t("뷰티 체험 팝업 이벤트 기획",         "beauty", "M", "오지현",  15,  "todo"),
        t("쿠션 파운데이션 시즌 구성 기획",      "beauty", "M", "강예진",   5,  "inprog"),
        t("향수 신제품 런칭 행사 준비",          "beauty", "H", "임수연",  14,  "todo"),
        t("뷰티 클래스 프로그램 기획",           "beauty", "M", "신채원",  25,  "todo"),
        # ── 잡화 (10) ────────────────────────────────────────────
        t("명품 핸드백 신규 입고 검수",          "accessories", "H", "이민지",   2,  "inprog"),
        t("잡화 플로어 VMD 여름 교체",           "accessories", "M", "박수현",   6,  "todo"),
        t("핸드백 브랜드 계약 갱신",             "accessories", "H", "정소영",  14,  "inprog"),
        t("여름 선글라스·스트로햇 기획전",        "accessories", "H", "김나영",   9,  "todo"),
        t("5월 잡화 매출 분석 보고",             "accessories", "H", "윤혜원",  -8,  "done",  True),
        t("신규 액세서리 브랜드 입점 협의",      "accessories", "M", "이민지",  20,  "todo"),
        t("명품관 핸드백 재고 현황 파악",        "accessories", "M", "박수현",  -5,  "done"),
        t("여름 잡화 특가 기획전 준비",          "accessories", "H", "정소영",  12,  "todo"),
        t("지갑·소품 신상 진열 기획",            "accessories", "M", "김나영",   4,  "inprog"),
        t("F/W 핸드백 소싱 계획 수립",           "accessories", "H", "윤혜원",  50,  "todo"),
        # ── 란제리 (10) ──────────────────────────────────────────
        t("여름 란제리 신상품 입고",             "lingerie", "M", "최지은",   3,  "inprog"),
        t("속옷 브랜드 계약 갱신",              "lingerie", "H", "서유리",  10,  "inprog"),
        t("여름 수영복 기획전 준비",             "lingerie", "H", "조민아",   8,  "todo"),
        t("란제리 VMD 여름 교체",               "lingerie", "M", "강지현",  -6,  "done"),
        t("5월 란제리 매출 분석",               "lingerie", "M", "임예진", -10,  "done"),
        t("수면 속옷 신규 라인 입점 검토",       "lingerie", "M", "최지은",  18,  "todo"),
        t("체형 보정 속옷 기획 상품 구성",       "lingerie", "H", "서유리",  12,  "todo"),
        t("여름 수영복 사이즈 재고 점검",        "lingerie", "M", "조민아",   2,  "inprog"),
        t("란제리 브랜드 팝업 이벤트 기획",      "lingerie", "M", "강지현",  22,  "todo"),
        t("속옷 고객 피팅 서비스 기획",          "lingerie", "L", "임예진",  28,  "todo"),
    ]


def seed_tasks_living():
    def t(title, cell, pri, assignee, due_offset, status, shared=False):
        return {"id": new_id(), "title": title, "cell": cell, "pri": pri,
                "assignee": assignee, "due": today_str(due_offset),
                "status": status, "desc": "", "shared": shared, "shared_branch": False}
    return [
        # ── 가전제품 (10) ────────────────────────────────────────
        t("삼성 가전 신상품 입고 검수",           "appliances", "H", "강준호",   2,  "inprog"),
        t("여름 에어컨 특가 기획전 준비",         "appliances", "H", "이성민",   7,  "todo"),
        t("LG전자 계약 갱신 협상",               "appliances", "H", "박재훈",  14,  "inprog"),
        t("가전 VMD 여름 시즌 교체",             "appliances", "M", "최동원",  -5,  "done"),
        t("5월 가전 매출 분석 보고",             "appliances", "H", "김성우", -10,  "done",  True),
        t("고가 가전 VIP 시연 행사 기획",        "appliances", "H", "강준호",  15,  "todo"),
        t("제습기·공기청정기 재고 점검",          "appliances", "M", "이성민",  -6,  "done"),
        t("로봇청소기 신규 브랜드 입점 협의",    "appliances", "M", "박재훈",  20,  "todo"),
        t("가전 제품 사후 서비스 개선 기획",     "appliances", "L", "최동원",  25,  "todo"),
        t("에어컨 설치 서비스 제휴 협의",        "appliances", "M", "김성우",   8,  "inprog"),
        # ── 생활용품 (10) ────────────────────────────────────────
        t("여름 생활용품 신상 입고 검수",         "living", "M", "정현우",   3,  "inprog"),
        t("생활용품 플로어 진열 재배치",          "living", "M", "한지민",   8,  "todo"),
        t("생활용품 브랜드 계약 갱신",            "living", "H", "서민준",  12,  "inprog"),
        t("여름 욕실용품 기획전 준비",            "living", "M", "오세진",  10,  "todo"),
        t("5월 생활용품 매출 분석",              "living", "H", "임진호",  -8,  "done"),
        t("친환경 생활용품 입점 협의",            "living", "M", "정현우",  20,  "todo"),
        t("청소용품 신상 라인 검토",              "living", "L", "한지민",  15,  "todo"),
        t("생활용품 재고 현황 조사",             "living", "M", "서민준",  -5,  "done"),
        t("향기·디퓨저 신규 브랜드 입점",        "living", "M", "오세진",   7,  "inprog"),
        t("여름 방충 용품 특가 행사 기획",        "living", "H", "임진호",  -3,  "done"),
        # ── 주방용품 (10) ────────────────────────────────────────
        t("르크루제 신상품 입고 검수",            "kitchen", "H", "김지훈",   2,  "inprog"),
        t("여름 주방용품 기획전 준비",            "kitchen", "H", "이준혁",   8,  "todo"),
        t("주방 가전 브랜드 계약 갱신",           "kitchen", "H", "박성호",  12,  "inprog"),
        t("주방용품 VMD 여름 교체",              "kitchen", "M", "최재훈",  -5,  "done"),
        t("5월 주방용품 매출 분석",              "kitchen", "H", "나민준", -10,  "done",  True),
        t("신규 쿡웨어 브랜드 입점 협의",        "kitchen", "M", "김지훈",  20,  "todo"),
        t("전기밥솥 신상 시연 행사 기획",        "kitchen", "H", "이준혁",  15,  "todo"),
        t("주방용품 재고 현황 파악",             "kitchen", "M", "박성호",  -7,  "done"),
        t("친환경 주방용품 기획전 준비",         "kitchen", "M", "최재훈",  18,  "todo"),
        t("여름 바베큐 용품 특가 기획",          "kitchen", "H", "나민준",  -3,  "done"),
        # ── 가구/인테리어 (10) ───────────────────────────────────
        t("여름 신상 가구 입고 검수",            "furniture", "H", "송재호",   3,  "inprog"),
        t("인테리어 소품 VMD 여름 교체",         "furniture", "M", "조민수",   8,  "todo"),
        t("가구 브랜드 계약 갱신",              "furniture", "H", "임태준",  14,  "inprog"),
        t("여름 리빙 인테리어 기획전",           "furniture", "H", "정현석",  10,  "todo"),
        t("5월 가구 매출 분석 보고",            "furniture", "H", "유재원", -10,  "done",  True),
        t("신규 북유럽 스타일 브랜드 입점",      "furniture", "M", "송재호",  25,  "todo"),
        t("가구 전시장 레이아웃 재배치",         "furniture", "M", "조민수",  12,  "inprog"),
        t("가구 재고 및 손상 현황 점검",         "furniture", "M", "임태준",  -5,  "done"),
        t("침실 인테리어 패키지 기획",           "furniture", "H", "정현석",  18,  "todo"),
        t("친환경 가구 라인 입점 협의",          "furniture", "M", "유재원",  28,  "todo"),
    ]


def seed_events_mens_sports():
    def e(title, offset, typ, note, cell=None, shared=True):
        return {"id": new_id(), "title": title, "date": today_str(offset),
                "type": typ, "note": note, "shared": shared,
                "shared_branch": False, "cell": cell, "source": "manual"}
    return [
        e("스포츠 브랜드 신상 발표회",          3,  "meeting",  "나이키·아디다스 참석"),
        e("여름 골프 특가 행사 오픈",           10,  "promo",    "7일간 진행"),
        e("아웃도어 캠핑 체험 이벤트",          15,  "promo",    "B1 특설 무대"),
        e("남성 패션 여름 컬렉션 런칭",          12,  "promo",    "4F 행사장", "mens_fashion"),
        e("팀 월간 영업 보고",                  -5,  "deadline", "팀장 보고"),
        e("골프 VIP 고객 초청 행사",            14,  "promo",    "VIP 100명", "golf"),
        e("남성스포츠팀 정기 회의",              5,  "meeting",  "전 셀 참석"),
        e("시즌오프 할인 행사 시작",            22,  "promo",    "전 셀 동시"),
    ]


def seed_events_womens():
    def e(title, offset, typ, note, cell=None, shared=True):
        return {"id": new_id(), "title": title, "date": today_str(offset),
                "type": typ, "note": note, "shared": shared,
                "shared_branch": False, "cell": cell, "source": "manual"}
    return [
        e("여성 패션 여름 컬렉션 발표",          8,  "promo",    "3F 전체"),
        e("뷰티 체험 팝업 행사",               12,  "promo",    "1F 코너", "beauty"),
        e("잡화·핸드백 특가 기획전",            10,  "promo",    "명품관 전체", "accessories"),
        e("VIP 여성 스타일링 행사",             18,  "promo",    "VIP 80명"),
        e("팀 월간 영업 보고",                  -5,  "deadline", "팀장 보고"),
        e("여성팀 브랜드 협의 미팅",             5,  "meeting",  "전 셀 참석"),
        e("여름 수영복 기획전 오픈",              9,  "promo",    "5F 비치 존", "lingerie"),
        e("패션 트렌드 리포트 발표",             25,  "deadline", "경영진 발표"),
    ]


def seed_events_living():
    def e(title, offset, typ, note, cell=None, shared=True):
        return {"id": new_id(), "title": title, "date": today_str(offset),
                "type": typ, "note": note, "shared": shared,
                "shared_branch": False, "cell": cell, "source": "manual"}
    return [
        e("여름 에어컨 특가 행사 오픈",          5,  "promo",    "전 층 동시"),
        e("삼성·LG 신상 가전 발표회",           8,  "meeting",  "브랜드 담당자"),
        e("주방용품 쿠킹 클래스 행사",          12,  "promo",    "요리 강사 초청", "kitchen"),
        e("가구 인테리어 기획전 오픈",           10,  "promo",    "6F 전체"),
        e("팀 월간 영업 보고",                  -5,  "deadline", "팀장 보고"),
        e("스마트홈 가전 체험존 오픈",           18,  "promo",    "4F 체험존", "appliances"),
        e("생활가전팀 월간 회의",                3,  "meeting",  "전 셀 참석"),
        e("생활가전팀 분기 보고",               30,  "deadline", "경영진 발표"),
    ]


def seed_memos_mens_sports():
    return [
        {"id": new_id(), "title": "6월 스포츠팀 회의록",
         "content": "참석: 팀장, 각 셀장\n\n- 여름 할인 행사 일정 확정\n- 골프 VIP 행사 준비 현황 공유\n- F/W 소싱 출장 일정 조율 필요",
         "date": today_str(0), "cell": "sports_gear", "shared": True, "shared_branch": False},
        {"id": new_id(), "title": "F/W 아웃도어 소싱 방향성",
         "content": "- 고어텍스 소재 제품 비중 확대\n- 경량화 트렌드 반영 필수\n- 협력사: 블랙야크, 노스페이스 우선",
         "date": today_str(-2), "cell": "outdoor", "shared": False, "shared_branch": False},
    ]


def seed_memos_womens():
    return [
        {"id": new_id(), "title": "뷰티 브랜드 입점 협의 결과",
         "content": "협의 브랜드: A뷰티, B코스메틱\n위치: 1F 뷰티 라운지\n입점 예정: 8월 초\n- 런칭 팝업 이벤트 함께 기획 예정",
         "date": today_str(-1), "cell": "beauty", "shared": True, "shared_branch": False},
        {"id": new_id(), "title": "VIP 여성 스타일링 행사 기획 메모",
         "content": "일시: 6월 18일 14:00\n대상: VIP 고객 80명\n구성: 패션 + 뷰티 + 잡화 스타일링 코너\n- 스타일리스트 3명 섭외 완료",
         "date": today_str(0), "cell": "womens_fashion", "shared": False, "shared_branch": False},
    ]


def seed_memos_living():
    return [
        {"id": new_id(), "title": "여름 에어컨 특가 행사 메모",
         "content": "기간: 6월 5~7일 (3일간)\n참여 브랜드: 삼성, LG, 위니아\n목표 매출: 전년 대비 +15%\n- 설치 제휴 업체 협약 완료",
         "date": today_str(0), "cell": "appliances", "shared": True, "shared_branch": False},
        {"id": new_id(), "title": "쿠킹 클래스 행사 기획",
         "content": "일시: 6월 12일 14:00\n장소: B1 주방관 체험존\n강사: 외부 셰프 초청\n- 르크루제·발라르기 제품 활용 시연",
         "date": today_str(-1), "cell": "kitchen", "shared": False, "shared_branch": False},
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
    existing = st.session_state.teams_data.get(tid, {})
    st.session_state.teams_data[tid] = {
        "cfg":         st.session_state.cfg,
        "tasks":       st.session_state.tasks,
        "events":      st.session_state.events,
        "memos":       st.session_state.memos,
        "files":       st.session_state.files,
        "board_posts": existing.get("board_posts", []),
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
                "cfg":         _build_team_cfg(DEFAULT_TEAMS["sales_planning"], branch_name),
                "tasks":       seed_tasks(),
                "events":      seed_events(),
                "memos":       seed_memos(),
                "files":       [],
                "board_posts": seed_board_posts(),
            },
            "support": {
                "cfg":         _build_team_cfg(DEFAULT_TEAMS["support"], branch_name),
                "tasks":       seed_tasks_support(),
                "events":      seed_events_support(),
                "memos":       seed_memos_support(),
                "files":       [],
                "board_posts": [],
            },
            "mens_sports": {
                "cfg":         _build_team_cfg(DEFAULT_TEAMS["mens_sports"], branch_name),
                "tasks":       seed_tasks_mens_sports(),
                "events":      seed_events_mens_sports(),
                "memos":       seed_memos_mens_sports(),
                "files":       [],
                "board_posts": [],
            },
            "womens": {
                "cfg":         _build_team_cfg(DEFAULT_TEAMS["womens"], branch_name),
                "tasks":       seed_tasks_womens(),
                "events":      seed_events_womens(),
                "memos":       seed_memos_womens(),
                "files":       [],
                "board_posts": [],
            },
            "living": {
                "cfg":         _build_team_cfg(DEFAULT_TEAMS["living"], branch_name),
                "tasks":       seed_tasks_living(),
                "events":      seed_events_living(),
                "memos":       seed_memos_living(),
                "files":       [],
                "board_posts": [],
            },
        }
        st.session_state.branch_board_posts = seed_branch_board_posts()

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
