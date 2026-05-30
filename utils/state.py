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
    def t(title, cell, pri, assignee, due_offset, status, shared=False):
        return {"id": new_id(), "title": title, "cell": cell, "pri": pri,
                "assignee": assignee, "due": today_str(due_offset),
                "status": status, "desc": "", "shared": shared, "shared_branch": False}

    return [
        # ── 마케팅 (20) ──────────────────────────────────────────
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
        t("고객 설문조사 결과 분석",              "marketing", "L", "김민준", -15,   "done"),
        t("뉴스레터 6월호 콘텐츠 제작",           "marketing", "M", "윤지수",   5,   "inprog"),
        t("옥외광고 소재 교체 업무 협의",          "marketing", "L", "박소영",  12,   "todo"),
        t("카카오 플러스친구 채널 점검",           "marketing", "L", "이현우", -20,   "done"),
        t("F/W 시즌 마케팅 방향 수립",            "marketing", "H", "정예린",  60,   "todo"),
        t("제휴 마케팅 파트너사 성과 검토",        "marketing", "M", "김민준",  -3,   "hold"),
        t("신규 고객 유치 캠페인 기획",           "marketing", "H", "윤지수",  25,   "todo"),
        t("시즌 MD 협업 마케팅 소재 제작",        "marketing", "M", "박소영",   7,   "inprog"),
        t("경쟁사 마케팅 동향 분석 리포트",        "marketing", "L", "이현우", -30,   "done"),
        t("연간 마케팅 예산 집행 정산",           "marketing", "H", "정예린", -45,   "done"),

        # ── 영업분석 (20) ────────────────────────────────────────
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
        t("연령대별 구매력 분석 보고서",          "analysis",  "M", "박지호",  22,   "todo"),
        t("온·오프라인 매출 채널 비교 분석",     "analysis",  "H", "이수민",   6,   "inprog", True),
        t("매장별 평균 객단가 분석",             "analysis",  "L", "최재원", -10,   "done"),
        t("계절별 매출 패턴 5개년 분석",         "analysis",  "L", "한지민",  75,   "todo"),
        t("카드사 제휴 실적 분기 분석",          "analysis",  "M", "오동현",   8,   "inprog"),
        t("멤버십 등급별 구매 행동 분석",        "analysis",  "M", "박지호",  18,   "todo"),
        t("2분기 사업 성과 종합 보고서 작성",    "analysis",  "H", "이수민",  30,   "todo",   True),
        t("고객 구매 패턴 변화 분석",            "analysis",  "M", "최재원", -25,   "done"),
        t("연간 매출 목표 달성률 점검",          "analysis",  "H", "한지민",   0,   "inprog"),
        t("이탈 고객 재유입 효과 측정",          "analysis",  "M", "오동현",  35,   "todo"),

        # ── 온라인 (20) ──────────────────────────────────────────
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
        t("스마트스토어 신규 상품 등록",          "online",    "L", "정도현",   4,   "inprog"),
        t("라이브커머스 7월 일정 조율",           "online",    "M", "강하늘",  25,   "todo"),
        t("온라인 재고 관리 시스템 점검",         "online",    "M", "서지원", -10,   "done"),
        t("디지털 고객 경험 개선 기획서 작성",    "online",    "H", "임채은",  20,   "todo"),
        t("앱 5.0 업데이트 출시 전 QA",          "online",    "H", "유태양",   6,   "inprog"),
        t("온라인 CS 응대 지침 개정",             "online",    "L", "정도현", -20,   "done"),
        t("결제 시스템 간헐적 오류 원인 파악",    "online",    "H", "강하늘",  -8,   "done"),
        t("디지털 쿠폰 발급 현황 월간 보고",      "online",    "L", "서지원",   9,   "todo"),
        t("온라인 배송 실적 분석 보고",           "online",    "M", "임채은", -18,   "done"),
        t("F/W 시즌 온라인 기획전 준비",          "online",    "H", "유태양",  55,   "todo"),

        # ── MD (20) ─────────────────────────────────────────────
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
        t("B브랜드 철수 대체 입점 브랜드 탐색",   "md",        "H", "오재원",  18,   "inprog"),
        t("브랜드 매출 순위 월간 보고 자료 작성", "md",        "M", "강지원",  -7,   "done",   True),
        t("식품관 구성 개편 방향 검토 보고서",    "md",        "M", "신민서",  28,   "todo"),
        t("명품관 리뉴얼 공사 업체 협의",         "md",        "H", "류준혁", -15,   "hold"),
        t("신규 브랜드 프로모션 협업 기획",       "md",        "M", "백서연",  16,   "todo"),
        t("신규 브랜드 NBO 작성 및 제출",        "md",        "H", "오재원", -10,   "done"),
        t("C브랜드 입점 계약서 법무 검토 요청",   "md",        "H", "강지원",   7,   "inprog"),
        t("6월 MD 팀 정기 회의 준비",            "md",        "L", "신민서",  -2,   "done"),
        t("글로벌 패션 브랜드 트렌드 조사",       "md",        "L", "류준혁",  40,   "todo"),
        t("F/W 시즌 의류 상품 소싱 계획",        "md",        "H", "백서연",  45,   "todo"),
    ]


def seed_tasks_support():
    def t(title, cell, pri, assignee, due_offset, status, shared=False):
        return {"id": new_id(), "title": title, "cell": cell, "pri": pri,
                "assignee": assignee, "due": today_str(due_offset),
                "status": status, "desc": "", "shared": shared, "shared_branch": False}

    return [
        # ── 인사파트 (20) ────────────────────────────────────────
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
        t("사회보험 6월 신고 처리",               "hr_part", "H", "이인사",   0,   "inprog"),
        t("직원 복지 포인트 2분기 정산",          "hr_part", "M", "김복지", -20,   "done"),
        t("신규 채용 합격자 입사 안내문 발송",    "hr_part", "M", "장채원",  10,   "todo"),
        t("인사 평가 시스템 고도화 검토",         "hr_part", "L", "송인국",  35,   "todo"),
        t("직원 경력개발 계획 수립 면담",         "hr_part", "M", "민지혜",   8,   "inprog"),
        t("하반기 팀빌딩 워크숍 일정 조율",       "hr_part", "M", "이인사",  45,   "todo"),
        t("고충 처리 위원회 3분기 운영 준비",     "hr_part", "L", "김복지",  30,   "todo"),
        t("직원 역량 강화 교육 과정 기획",        "hr_part", "M", "장채원",  22,   "todo"),
        t("3분기 인력 충원 계획 수립",            "hr_part", "H", "송인국",   6,   "inprog", True),
        t("인사 규정 개정안 초안 검토",           "hr_part", "M", "민지혜",  28,   "todo"),

        # ── 지원파트 (20) ────────────────────────────────────────
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
        t("전기 요금 절감 방안 보고서 작성",      "support_part", "L", "박지원", -12,   "done"),
        t("보안 시스템 업그레이드 기획서 작성",   "support_part", "H", "최관리",  25,   "todo"),
        t("매장 내 안전사고 예방 교육 실시",      "support_part", "M", "한재형",  -8,   "done"),
        t("외부 업체 관리 대장 상반기 업데이트",  "support_part", "L", "임소연",   4,   "inprog"),
        t("고객 편의시설 운영 현황 점검",         "support_part", "L", "조성민",  15,   "todo"),
        t("직원 휴게실 리뉴얼 계획 수립",         "support_part", "M", "박지원",  30,   "todo"),
        t("고객 화장실 위생 관리 체계 강화",      "support_part", "M", "최관리",  -6,   "done"),
        t("비품 자산 대장 상반기 정리",           "support_part", "M", "한재형",   6,   "inprog"),
        t("매장 음향·방송 시스템 점검",          "support_part", "L", "임소연",  22,   "todo"),
        t("연간 시설 유지보수 계획 수립",         "support_part", "H", "조성민",  40,   "todo"),
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
        e("7월 KPI 목표 설정 회의",         20,  "meeting",  "팀장 주재"),
        e("온라인몰 앱 5.0 업데이트 출시",  6,   "promo",    "앱스토어 배포",       "online",  False),
        e("신규 브랜드 입점 협의 미팅",      1,   "meeting",  "C브랜드 담당자",      "md",      False),
        e("5월 월간 매출 보고",            -5,   "deadline", "경영진 보고",         None,       True),
        e("팀장 리더십 워크숍",           -20,   "meeting",  "외부 교육장"),
        e("추석 프로모션 기획 착수 회의",   45,  "meeting",  "전 셀 참여"),
        e("F/W 시즌 MD 협업 회의",         50,  "meeting",  "MD·마케팅 합동"),
        e("2분기 사업 성과 보고회",         30,  "deadline", "경영진 발표"),
        e("카드사 제휴 실적 보고",           8,  "deadline", "제휴팀 미팅",         "analysis", False),
        e("라이브커머스 7월 첫 방송",       25,  "promo",    "인플루언서 협업",     "online"),
        e("가을 컬렉션 런칭 행사",          65,  "promo",    "3F 특설 행사장"),
        e("연간 마케팅 예산 리뷰",          35,  "deadline", "기획팀장 보고",       "marketing"),
        e("6월 인스타그램 라이브 방송",     12,  "promo",    "팔로워 이벤트",       "marketing", False),
        e("명품관 리뉴얼 완공 기념 행사",   40,  "promo",    "바이어 초청"),
        e("하반기 사업 계획 수립 회의",     55,  "meeting",  "전체 팀 참여"),
        e("온라인 여름 기획전 오픈",         9,  "promo",    "72시간 특가",         "online"),
        e("MD 브랜드 소싱 출장",           -12,  "etc",      "서울 패션위크",       "md",      False),
        e("전사 고객 서비스 교육",         -10,  "meeting",  "전 직원 필수 참석"),
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
        e("엘리베이터 정기 검사",         12,  "deadline", "검사 기관 방문",       None,  False),
        e("냉난방 설비 하절기 점검",       3,  "deadline", "전문 업체 방문",       None,  False),
        e("상반기 인사 평가 마감",         20,  "deadline", "평가 시스템 제출",    "hr_part"),
        e("신입 직원 온보딩 교육",         5,  "meeting",  "1일 교육 과정",       "hr_part"),
        e("LED 교체 공사 시작",            9,  "etc",      "3일간 야간 작업",     None,  False),
        e("폐기물 처리 계약 만료",         20,  "deadline", "갱신 협의 필요",      None,  False),
        e("하반기 인력 충원 계획 보고",    40,  "meeting",  "경영진 보고",         "hr_part"),
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
            r("🦉", "부엉이", "모두 수고하세요~", "05.28 15:20"),
          ]),
        p("🐯", "호랑이", "요즘 야근이 너무 많은 것 같아요. 업무 분배가 좀 더 효율적으로 이루어졌으면 좋겠습니다. 솔직히 번아웃 올 것 같아요.",
          "05.27 10:20", likes=5, replies=[
            r("🦦", "수달", "맞아요 저도 같은 생각이에요. 팀장님께 말씀드려보는 건 어떨까요", "05.27 11:00"),
          ]),
        p("🐧", "펭귄", "팀 회식 언제 하나요? 오래됐는데... 다들 바빠서 날 잡기가 어렵죠 ㅎㅎ 한 번 편하게 모이고 싶어요.",
          "05.26 16:45", likes=9, replies=[
            r("🦝", "너구리", "저도 기대하고 있어요! 빨리 날 잡혔으면 좋겠네요", "05.26 17:10"),
            r("🐨", "코알라", "찬성!! 꼭 성사됐으면 해요", "05.26 18:00"),
          ]),
        p("🦁", "사자", "카페테리아 커피머신이 또 고장났는데 이거 진짜 너무 자주 고장나지 않나요? 수리 요청 빨리 해주셨으면 합니다.",
          "05.24 11:00", likes=4),
        p("🐼", "판다", "오늘 팀장님한테 칭찬 들었는데 익명으로라도 기분 좋다고 말하고 싶어서요 ㅎㅎ 좋은 하루 되세요! 모두 화이팅~",
          "05.22 14:30", likes=12, replies=[
            r("🐬", "돌고래", "저도 들었어요~ 다들 고생하셨어요!", "05.22 15:00"),
          ]),
        p("🦔", "고슴도치", "층별로 다른 프로모션 테마를 적용하면 어떨까요? 고객 동선 유도가 훨씬 자연스러울 것 같아서요. 다음 기획 회의 때 한번 제안해볼까요?",
          "05.20 09:15", likes=6, replies=[
            r("🦋", "나비", "좋은 아이디어인데요! 한번 제안해봐도 좋을 것 같아요.", "05.20 10:30"),
            r("🦚", "공작", "저도 비슷한 생각 했어요. 꼭 올려봐요!", "05.20 11:45"),
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
            r("🐿️", "다람쥐", "저도 개인적으로 바라고 있었어요!", "05.28 17:00"),
          ]),
        p("🦭", "물개", "고객 주차 안내 시스템이 좀 더 직관적이었으면 좋겠습니다. 처음 오시는 분들이 많이 헤매시더라고요.",
          "05.27 11:15", likes=6),
        p("🦋", "나비", "1층 고객 화장실 청결 상태가 많이 아쉽습니다. 주말에 특히 관리가 잘 안 되는 것 같아요. 개선해주세요.",
          "05.25 14:00", likes=10, replies=[
            r("🐸", "개구리", "저도 느꼈어요. 빨리 개선되었으면 합니다.", "05.25 14:30"),
          ]),
        p("🦅", "독수리", "매장 내 음악이 너무 크다는 고객 피드백이 많습니다. 볼륨 조절 기준을 정해두면 좋을 것 같아요.",
          "05.23 09:20", likes=7),
        p("🦩", "홍학", "직원 휴게실에 전자레인지 하나 더 배치해주시면 정말 좋겠습니다. 점심 시간에 항상 줄이 길어요.",
          "05.21 15:30", likes=13, replies=[
            r("🦌", "사슴", "완전 공감입니다. 꼭 반영되었으면 해요", "05.21 16:00"),
          ]),
        p("🐘", "코끼리", "전 직원 대상 CS 교육이 좀 더 자주 이루어지면 좋겠습니다. 고객 응대 수준이 팀마다 다르게 느껴져서요.",
          "05.19 10:00", likes=5, replies=[
            r("🦒", "기린", "동의합니다. 통일된 기준이 필요할 것 같아요", "05.19 10:45"),
          ]),
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
