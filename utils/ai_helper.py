"""
utils/ai_helper.py
Google Gemini REST API 직접 호출 (requests 사용 — SDK 비의존)
"""
import streamlit as st
import json
import requests
from datetime import date, timedelta
from utils.state import EV_TYPES

_GEMINI_BASE = "https://generativelanguage.googleapis.com/v1beta/models"
_MODEL       = "gemini-2.0-flash"


def _get_api_key() -> str:
    """API 키 조회 순서: session_state → secrets.toml → 환경변수"""
    runtime_key = st.session_state.get("runtime_api_key", "")
    if runtime_key:
        return runtime_key
    try:
        key = st.secrets.get("GEMINI_API_KEY", "")
    except Exception:
        key = ""
    if not key:
        import os
        key = os.environ.get("GEMINI_API_KEY", "")
    return key


def _call_gemini(prompt: str, system: str = "", max_tokens: int = 1000) -> str:
    """Gemini generateContent API를 requests로 직접 호출 (단일 turn)"""
    key = _get_api_key()
    if not key:
        raise ValueError("GEMINI_API_KEY가 설정되지 않았습니다.")

    body: dict = {
        "contents": [{"role": "user", "parts": [{"text": prompt}]}],
        "generationConfig": {"maxOutputTokens": max_tokens, "temperature": 0.7},
    }
    if system:
        body["systemInstruction"] = {"parts": [{"text": system}]}

    resp = requests.post(
        f"{_GEMINI_BASE}/{_MODEL}:generateContent?key={key}",
        json=body,
        timeout=30,
    )

    if not resp.ok:
        try:
            err = resp.json().get("error", {})
            msg = err.get("message", "")
        except Exception:
            msg = resp.text[:200]

        if resp.status_code in (400, 401, 403):
            raise Exception("API 키가 유효하지 않습니다. Gemini API 키를 다시 확인해주세요.")
        elif resp.status_code == 429:
            raise Exception("Gemini 무료 플랜 요청 한도에 잠시 걸렸습니다. 1분 후 다시 시도해주세요.")
        else:
            raise Exception(f"API 오류 ({resp.status_code}): {msg[:100] or resp.reason}")

    candidates = resp.json().get("candidates", [])
    if not candidates:
        raise Exception("Gemini 응답이 비어있습니다. 다시 시도해주세요.")
    return candidates[0]["content"]["parts"][0]["text"]


def _call_gemini_chat(messages: list[dict], system: str = "", max_tokens: int = 1000) -> str:
    """멀티턴 채팅용 Gemini 호출.
    messages는 {"role": "user" | "assistant", "content": "..."} 형식."""
    key = _get_api_key()
    if not key:
        raise ValueError("GEMINI_API_KEY가 설정되지 않았습니다.")

    # OpenAI 형식 → Gemini 형식 변환 (assistant → model)
    contents = []
    for m in messages:
        role = "model" if m["role"] == "assistant" else "user"
        contents.append({"role": role, "parts": [{"text": m["content"]}]})

    body: dict = {
        "contents": contents,
        "generationConfig": {"maxOutputTokens": max_tokens, "temperature": 0.7},
    }
    if system:
        body["systemInstruction"] = {"parts": [{"text": system}]}

    resp = requests.post(
        f"{_GEMINI_BASE}/{_MODEL}:generateContent?key={key}",
        json=body,
        timeout=30,
    )

    if not resp.ok:
        try:
            err = resp.json().get("error", {})
            msg = err.get("message", "")
        except Exception:
            msg = resp.text[:200]

        if resp.status_code in (400, 401, 403):
            raise Exception("API 키가 유효하지 않습니다.")
        elif resp.status_code == 429:
            raise Exception("Gemini 무료 플랜 요청 한도에 잠시 걸렸습니다. 1분 후 다시 시도해주세요.")
        else:
            raise Exception(f"API 오류 ({resp.status_code}): {msg[:100] or resp.reason}")

    candidates = resp.json().get("candidates", [])
    if not candidates:
        raise Exception("Gemini 응답이 비어있습니다.")
    return candidates[0]["content"]["parts"][0]["text"]


# 하위 호환 (admin_view에서 import)
def get_client():
    return bool(_get_api_key())


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
        f"상태:{'대기' if t['status']=='todo' else '진행중' if t['status']=='inprog' else '완료' if t['status']=='done' else '보류'}"
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
    """오늘의 AI 체크리스트 생성."""
    if not _get_api_key():
        return [
            {"icon": "🔑", "text": "AI 기능을 사용하려면 GEMINI_API_KEY를 설정하세요.", "level": "normal"},
            {"icon": "📋", "text": "영업기획팀 어드민 > AI API 키 설정에서 입력하세요.", "level": "normal"},
        ]

    ctx = build_team_context()
    prompt = f"""당신은 롯데백화점 인천점 AI 어시스턴트입니다.
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
        text = _call_gemini(prompt, max_tokens=800)
        text = text.replace("```json", "").replace("```", "").strip()
        return json.loads(text)
    except Exception as e:
        return [{"icon": "⚠️", "text": f"AI 연결 오류: {str(e)[:60]}", "level": "urgent"}]


def get_ai_task_advice(task: dict) -> list[dict]:
    """특정 Task에 대한 AI 조언 생성 — JSON 배열 형식 (체크리스트와 동일 구조)"""
    if not _get_api_key():
        return [{"icon": "🔑", "text": "AI 기능을 사용하려면 GEMINI_API_KEY를 설정하세요.", "level": "normal"}]

    cfg       = st.session_state.get("cfg", {})
    units     = cfg.get("units", {})
    cell_name = units.get(task.get("cell", ""), {}).get("name", task.get("cell", ""))
    ctx       = build_team_context()

    status_labels = {"todo": "대기", "inprog": "진행중", "done": "완료", "hold": "보류"}
    pri_labels    = {"H": "높음", "M": "보통", "L": "낮음"}

    prompt = f"""당신은 롯데백화점 인천점 AI 어드바이저입니다.
다음 업무에 대한 AI 조언을 JSON 배열로만 응답하세요 (설명 없이).

=== 대상 업무 ===
제목: {task.get('title', '')}
담당 조직: {cell_name}
담당자: {task.get('assignee', '미정')}
마감일: {task.get('due', '미정')}
우선순위: {pri_labels.get(task.get('pri', 'M'), '보통')}
현재 상태: {status_labels.get(task.get('status', 'todo'), '대기')}
세부 내용: {task.get('desc', '없음')}

=== 팀 전체 현황 ===
{ctx}

규칙:
- 정확히 4개 항목
- JSON 배열로만 응답 (설명 없이)
- 형식: [{{"icon":"이모지","text":"조언 내용 1~2문장","level":"urgent|normal|ok"}}]
- level 기준: urgent(리스크·긴급 대응), normal(실행 전략·트렌드), ok(순조·긍정 인사이트)
- icon 권장: 💡(실행전략) 📈(트렌드&인사이트) ⚠️(리스크) 🏆(참고사례)
- 한국어로 간결하고 실용적으로"""

    try:
        text = _call_gemini(prompt, max_tokens=600)
        text = text.replace("```json", "").replace("```", "").strip()
        return json.loads(text)
    except Exception as e:
        return [{"icon": "⚠️", "text": f"AI 조언 오류: {str(e)[:60]}", "level": "urgent"}]


def get_ai_memo_advice(memo_title: str, memo_content: str) -> str:
    """메모/회의록에 대한 AI 조언 생성 (사회·경제·문화 인사이트 포함)"""
    if not _get_api_key():
        return "AI 기능을 사용하려면 GEMINI_API_KEY를 설정하세요."

    ctx = build_team_context()

    prompt = f"""당신은 롯데백화점 인천점 비즈니스 어드바이저입니다.
다음 메모/회의록에 대해 전문적인 조언과 인사이트를 제공해주세요.

=== 메모 내용 ===
제목: {memo_title}
내용:
{memo_content}

=== 팀 전체 현황 ===
{ctx}

위 메모 내용에 대해 아래 관점에서 조언해주세요:
• 💡 핵심 인사이트: 이 메모의 가장 중요한 전략적 포인트
• 📊 데이터 & 근거: 주요 결정을 뒷받침할 업계 데이터나 사례
• 🔗 연관 업무: 현재 팀 Task·일정과의 연계 가능성
• ⚠️ 리스크 & 고려사항: 놓칠 수 있는 리스크나 추가 검토 사항
• 🌐 외부 환경: 관련 사회·경제·소비 트렌드나 경쟁 환경 변화

한국어로 간결하고 실용적으로 작성하세요."""

    try:
        return _call_gemini(prompt, max_tokens=700)
    except Exception as e:
        return f"⚠️ AI 조언 오류: {str(e)[:80]}"


def chat_with_advisor(user_message: str, history: list[dict]) -> str:
    """AI 어드바이저 채팅 응답"""
    if not _get_api_key():
        return "⚠️ AI 기능을 사용하려면 GEMINI_API_KEY를 설정하세요."

    ctx   = build_team_context()
    user  = st.session_state.get("user", {})
    cfg   = st.session_state.get("cfg", {})
    units = cfg.get("units", {})
    unit_name = units.get(user.get("cell", ""), {}).get("name", user.get("cell", ""))

    system = f"""당신은 롯데백화점 인천점 AI 어드바이저입니다.
현재 사용자: {user.get('name','미상')} ({unit_name})
팀 구성: {', '.join(u['name'] for u in units.values())} (팀장 포함)

{ctx}

위 팀 내부 데이터와 함께 외부 유통업계 트렌드·마케팅 사례·전략 등을 활용해
실질적이고 구체적인 조언을 제공하세요. 한국어로 친절하고 전문적으로 답변하세요."""

    messages = history[-10:] + [{"role": "user", "content": user_message}]

    try:
        return _call_gemini_chat(messages, system=system, max_tokens=1000)
    except Exception as e:
        return f"⚠️ AI 오류가 발생했습니다: {str(e)[:100]}"


def extract_action_items(memo_content: str) -> str:
    """메모에서 Action Item 추출"""
    if not _get_api_key():
        return "⚠️ AI 기능을 사용하려면 GEMINI_API_KEY를 설정하세요."

    prompt = f"""다음 메모에서 Action Item을 최대 5개 추출하세요.
형식: "• [담당자]: [할일] (마감: [날짜/시기])"
담당자나 마감이 불명확하면 "미정"으로 표기.
설명 없이 목록만 출력.

{memo_content}"""

    try:
        return _call_gemini(prompt, max_tokens=500)
    except Exception as e:
        return f"AI 오류: {str(e)[:80]}"
