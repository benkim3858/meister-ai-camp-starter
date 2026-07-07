# -*- coding: utf-8 -*-
"""
AI 캠프 챗봇 스타터 템플릿
실행:  python app.py  →  브라우저에서 http://localhost:7860 열림
"""

# ╔══════════════════════════════════════════════════════════════╗
# ║ [1] 여기만 수정하세요 — 이 세 가지가 여러분 팀의 '하네스'입니다 ║
# ╚══════════════════════════════════════════════════════════════╝

SERVICE_NAME = "우리 팀 AI 서비스"  # 챗봇 이름 (화면 제목에 표시)

SYSTEM_PROMPT = """너는 친절한 AI 도우미다.

규칙:
- 한국어로 답한다.
- 모르는 것은 모른다고 솔직하게 말한다.
- 답은 3문장 이내로 간결하게 한다.
"""  # ← 팀에서 설계한 시스템 프롬프트로 교체하세요

USE_KNOWLEDGE = True  # knowledge.md 문서를 참고해서 답할지 여부 (True/False)


# ──────────────────────────────────────────────────────────────────
# [2] 아래는 수정하지 않아도 됩니다 (읽어보는 것은 환영합니다)
#     하는 일: .env 로드 → 문서 주입 → AI 호출(3단 자동 전환) → 채팅 화면
# ──────────────────────────────────────────────────────────────────
import os
import pathlib

HERE = pathlib.Path(__file__).parent


def load_env():
    """같은 폴더의 .env 파일에서 API 키를 읽어 환경변수로 등록한다."""
    env_path = HERE / ".env"
    if env_path.exists():
        for line in env_path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, _, value = line.partition("=")
                os.environ.setdefault(key.strip(), value.strip())


load_env()

import gradio as gr  # noqa: E402
from openai import OpenAI  # noqa: E402

# 백엔드 3단 구성: 위에서부터 시도하고, 실패하면 자동으로 다음으로 넘어간다.
# (수업 원칙: 무료 클라우드가 막혀도 내 컴퓨터의 로컬 모델로 수업은 계속된다)
BACKENDS = [
    {
        "name": "Gemini (무료 클라우드)",
        "base_url": "https://generativelanguage.googleapis.com/v1beta/openai/",
        "api_key_env": "GOOGLE_API_KEY",
        "model": "gemini-2.5-flash",
    },
    {
        "name": "Groq (무료 클라우드)",
        "base_url": "https://api.groq.com/openai/v1",
        "api_key_env": "GROQ_API_KEY",
        "model": "llama-3.1-8b-instant",
    },
    {
        "name": "Ollama (내 컴퓨터)",
        "base_url": "http://localhost:11434/v1",
        "api_key_env": None,  # 로컬은 키가 필요 없다
        "model": "gemma3:4b",
    },
]


def build_system_prompt() -> str:
    """시스템 프롬프트에 knowledge.md 문서를 덧붙인다(초간단 RAG: 통째로 주입)."""
    prompt = SYSTEM_PROMPT
    if USE_KNOWLEDGE:
        kpath = HERE / "knowledge.md"
        if kpath.exists():
            knowledge = kpath.read_text(encoding="utf-8").strip()
            if knowledge:
                prompt += (
                    "\n\n[참고 문서]\n" + knowledge +
                    "\n\n위 참고 문서에 근거해서 답하라. 문서에 없는 내용은 지어내지 말라."
                )
    return prompt


def history_to_messages(history) -> list:
    """Gradio가 주는 대화 기록을 API 형식으로 변환한다(신·구 형식 모두 지원)."""
    messages = []
    for turn in history or []:
        if isinstance(turn, dict) and turn.get("role") in ("user", "assistant"):
            content = turn.get("content")
            if isinstance(content, str) and content:
                messages.append({"role": turn["role"], "content": content})
        elif isinstance(turn, (list, tuple)) and len(turn) == 2:
            user_msg, bot_msg = turn
            if user_msg:
                messages.append({"role": "user", "content": str(user_msg)})
            if bot_msg:
                messages.append({"role": "assistant", "content": str(bot_msg)})
    return messages


def explain_error(backend: dict, error: Exception) -> str:
    """오류를 학생이 스스로 조치할 수 있는 한국어 안내로 바꾼다."""
    text = str(error)
    if "키 없음" in text:
        return f"{backend['api_key_env']}가 .env 파일에 없습니다 → .env를 확인하세요"
    if "401" in text or "invalid" in text.lower() or "unauthorized" in text.lower():
        return "API 키가 잘못되었습니다 → .env의 키 값을 다시 확인하세요"
    if "429" in text or "rate" in text.lower() or "quota" in text.lower():
        return "무료 사용량 한도를 초과했습니다 → 잠시 후 재시도 (자동으로 다음 백엔드로 전환됨)"
    if "Connection" in text or "connect" in text.lower():
        if backend["api_key_env"] is None:
            return "Ollama가 실행 중이 아닙니다 → Ollama 앱을 켜거나 터미널에서 `ollama serve` 실행"
        return "서버에 연결하지 못했습니다 → 인터넷/방화벽 확인"
    return text[:120]


def ask_backend(backend: dict, messages: list) -> str:
    """백엔드 하나에 질문을 보내고 답을 받는다."""
    api_key = "not-needed"  # Ollama용 (아무 값이나 허용)
    if backend["api_key_env"]:
        api_key = os.environ.get(backend["api_key_env"], "").strip()
        if not api_key:
            raise RuntimeError("키 없음")
    client = OpenAI(base_url=backend["base_url"], api_key=api_key, timeout=60)
    response = client.chat.completions.create(
        model=backend["model"],
        messages=messages,
    )
    return response.choices[0].message.content


def chat(message, history):
    """채팅 화면이 호출하는 함수: 3단 백엔드를 순서대로 시도한다."""
    messages = [{"role": "system", "content": build_system_prompt()}]
    messages += history_to_messages(history)
    messages.append({"role": "user", "content": str(message)})

    failures = []
    for backend in BACKENDS:
        try:
            answer = ask_backend(backend, messages)
            if answer:
                return answer
            failures.append(f"• {backend['name']}: 빈 응답")
        except Exception as error:  # noqa: BLE001 — 수업용: 어떤 오류든 다음 백엔드로
            failures.append(f"• {backend['name']}: {explain_error(backend, error)}")

    return (
        "⚠️ 모든 백엔드 연결에 실패했습니다.\n\n"
        + "\n".join(failures)
        + "\n\n조치 순서: ① .env에 키가 있는지 ② 인터넷이 되는지 ③ Ollama가 켜져 있는지 확인 → 그래도 안 되면 선생님을 부르세요."
    )


if __name__ == "__main__":
    try:
        demo = gr.ChatInterface(fn=chat, title=SERVICE_NAME, type="messages")
    except TypeError:  # 구버전/신버전 Gradio에서 type 인자가 없는 경우
        demo = gr.ChatInterface(fn=chat, title=SERVICE_NAME)
    demo.launch()
