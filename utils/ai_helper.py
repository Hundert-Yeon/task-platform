"""
utils/ai_helper.py
Anthropic API 호출 헬퍼
"""
import streamlit as st
import json
from datetime import date, timedelta
from utils.state import EV_TYPES


def _get_api_key() -> str:
    """API 키 조회 순서: session_state(어드민 입력) → secrets.toml → 환경변수"""
    # 어드민에서 런타임 입력한 키가 있으면 최우선 사용
    runtime_key = st.session_state.get("runtime_api_key", "")
    if runtime_key:
        return runtime_key
    # secrets.toml
    try:
        key = st.secrets.get("ANTHROPIC_API_KEY", "")
    except Exception:
        key = ""
    # 환경변수
    if not key:
        import os
        key = os.environ.get("ANTHROPIC_API_KEY", "")
    return key


def get_client():
    """Anthropic 클라이언트. API 키가 없으면 None 반환."""
    key = _get_api_key()
    if not key:
        return None
    try:
        import anthropic
        return anthropic.Anthropic(api_key=key)
    except Exception:
        return None


def build_team_context() -> str:
    """현재 팀 전체 데이터를 컨텍스트 문자열로 빌드"""
    tasks  = st.session_state.get("tasks", [])
    events = st.session_state.get("events", [])
    memos  = st.session_state.get("memos", [])
    cfg    = st.session_state.get("cfg", {})
    units  = cfg.get("units", {})

    today = date.today()
    in3   = today + timedelta(days=3)

    def unit_name(uid):
        return units.get(uid, {}).get("name", uid)

    tasks_txt = "\n".join(
        f"- [{unit_name(t['cell'])}] {t['title']} | 마감:{t['due']} | "
        f"담당:{t.get('assignee','미정')} | "
        f"상태:{'대기' if t['status']=='todo' else '진행중' if t['status']=='inprog' else '완료' if t['status']=='done' else '보류'} | "
        f"공유:{'Y' if t.get('shared') else 'N'}"
        for t in tasks
    ) or "없음"

    manual_events = [e for e in events if e.get("source") == "manual"]
    events_txt = "\n".join(
        f"- {e['title']} | {e['date']} | {EV_TYPES.get(e['type'], e['type'])}"
        for e in manual_events
    ) or "없음"

    memos_txt = "\n---\n".join(
        f"[{m['title']}]: {m['content'][:200]}" for m in memos
    ) or "없음"

    return f"""
오늘 날짜: {today.isoformat()}
점·팀: {cfg.get('branch_name','')} {cfg.get('team_name','')}

=== 전체 Task 현황 ===
{tasks_txt}

=== 등록된 일정 ===
{events_txt}

=== 메모/회의록 ===
{memos_txt}

=== 통계 ===
전체: {len(tasks)}건, 진행중: {sum(1 for t in tasks if t['status']=='inprog')}건,
완료: {sum(1 for t in tasks if t['status']=='done')}건,
마감임박(3일): {sum(1 for t in tasks if t['status']!='done' and t.get('due','')<=in3.isoformat())}건
"""


def get_ai_checklist() -> list[dict]:
    """오늘의 AI 체크리스트 생성. API 키 없으면 안내 항목 반환."""
    client = get_client()
    if client is None:
        return [
            {"icon": "🔑", "text": "AI 기능을 사용하려면 ANTHROPIC_API_KEY를 설정하세요.", "level": "normal"},
            {"icon": "📋", "text": ".streamlit/secrets.toml 에 ANTHROPIC_API_KEY = \"sk-...\" 추가", "level": "normal"},
        ]

    ctx = build_team_context()
    prompt = f"""당신은 롯데백화점 인천점 영업기획팀 AI 어시스턴트입니다.
아래 팀 업무 현황을 분석해서 "TODAY'S AI CHECKLIST"를 작성하세요.

규칙:
- 정확히 4~5개 항목
- JSON 배열로만 응답 (설명 없이)
- 형식: [{{"icon":"이모지","text":"체크사항 내용","level":"urgent|normal|ok"}}]
- urgent: 오늘~내일 마감 또는 지연
- normal: 이번주 내 처리 필요
- ok: 순조롭게 진행 중

{ctx}"""

    try:
        response = client.messages.create(
            model="claude-sonnet-4-5",
            max_tokens=800,
            messages=[{"role": "user", "content": prompt}]
        )
        text = response.content[0].text.strip()
        text = text.replace("```json", "").replace("```", "").strip()
        return json.loads(text)
    except Exception as e:
        return [
            {"icon": "⚠️", "text": f"AI 연결 오류: {str(e)[:60]}", "level": "urgent"}
        ]


def chat_with_advisor(user_message: str, history: list[dict]) -> str:
    """AI 어드바이저 채팅 응답"""
    client = get_client()
    if client is None:
        return "⚠️ AI 기능을 사용하려면 ANTHROPIC_API_KEY를 설정하세요."

    ctx = build_team_context()
    user = st.session_state.get("user", {})
    cfg  = st.session_state.get("cfg", {})
    units = cfg.get("units", {})
    unit_name = units.get(user.get("cell",""), {}).get("name", user.get("cell",""))

    system = f"""당신은 롯데백화점 인천점 영업기획팀 AI 어드바이저입니다.
현재 사용자: {user.get('name','미상')} ({unit_name})
팀 구성: {', '.join(u['name'] for u in units.values())} (팀장 포함)

{ctx}

위 팀 내부 데이터와 함께 외부 유통업계 트렌드·마케팅 사례·전략 등을 활용해
실질적이고 구체적인 조언을 제공하세요. 한국어로 친절하고 전문적으로 답변하세요."""

    messages = history[-10:] + [{"role": "user", "content": user_message}]

    try:
        response = client.messages.create(
            model="claude-sonnet-4-5",
            max_tokens=1000,
            system=system,
            messages=messages,
        )
        return response.content[0].text
    except Exception as e:
        return f"⚠️ AI 오류가 발생했습니다: {str(e)[:100]}"


def extract_action_items(memo_content: str) -> str:
    """메모에서 Action Item 추출"""
    client = get_client()
    if client is None:
        return "⚠️ AI 기능을 사용하려면 ANTHROPIC_API_KEY를 설정하세요."

    try:
        response = client.messages.create(
            model="claude-sonnet-4-5",
            max_tokens=500,
            messages=[{
                "role": "user",
                "content": f"""다음 메모에서 Action Item을 최대 5개 추출하세요.
형식: "• [담당자]: [할일] (마감: [날짜/시기])"
담당자나 마감이 불명확하면 "미정"으로 표기.
설명 없이 목록만 출력.

{memo_content}"""
            }]
        )
        return response.content[0].text
    except Exception as e:
        return f"AI 오류: {str(e)[:80]}"
