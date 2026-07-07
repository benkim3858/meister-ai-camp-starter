# AI 캠프 챗봇 스타터 (Gradio Starter)

**받자마자 실행되는 챗봇**입니다. 여러분은 챗봇 껍데기를 코딩하는 대신,
파일 맨 위의 세 가지(이름·시스템 프롬프트·참고 문서)를 바꿔서
**자기 팀의 AI 서비스**를 만듭니다. 이 세 가지를 설계하는 일이 바로
이번 캠프에서 배우는 **하네스 엔지니어링**입니다.

## 빠른 시작 (10분)

```bash
# 1. 받기
git clone https://github.com/benkim3858/meister-ai-camp-starter.git
cd meister-ai-camp-starter

# 2. 라이브러리 설치 (2개뿐)
pip install -r requirements.txt

# 3. 키 넣기 — .env.example을 복사해 .env를 만들고 팀 키 붙여넣기
#    (Mac)     cp .env.example .env
#    (Windows) copy .env.example .env

# 4. 실행 → 브라우저에서 http://localhost:7860
python app.py
```

## 파일 구성

| 파일 | 역할 | 수정? |
|---|---|---|
| `app.py` | 챗봇 본체. **맨 위 [1]구역만 수정** | [1]구역만 |
| `knowledge.md` | 챗봇이 근거로 삼는 문서 | 팀 문서로 교체 |
| `.env.example` | API 키 칸 견본 (`.env`로 복사해서 사용) | 복사 후 키 입력 |
| `requirements.txt` | 설치 목록 (gradio, openai) | 그대로 |

## 동작 방식 (알아두면 좋은 것)

- **백엔드 3단 자동 전환**: Gemini → 안 되면 Groq → 안 되면 내 컴퓨터의 Ollama.
  무료 사용량이 떨어져도 챗봇이 죽지 않습니다.
- **문서 주입(RAG)**: `USE_KNOWLEDGE = True`면 `knowledge.md` 내용이
  시스템 프롬프트에 붙어서, 챗봇이 그 문서에 근거해 답합니다.
- **키는 코드에 없음**: 키는 `.env`에만 둡니다. `.env`는 git에 올라가지
  않도록 이미 막아뒀습니다(`.gitignore`). 배포(HF Spaces) 때는
  Settings > Secrets에 같은 이름으로 등록하면 됩니다.

## 문제 해결

| 증상 | 조치 |
|---|---|
| "GOOGLE_API_KEY가 .env에 없습니다" | `.env` 파일이 있는지, 키 이름 철자가 맞는지 확인 |
| "무료 사용량 한도 초과" | 자동으로 다음 백엔드로 넘어감. 계속되면 팀 내 동시 실행을 줄이기 |
| "Ollama가 실행 중이 아닙니다" | Ollama 앱 실행 또는 터미널에서 `ollama serve` |
| 화면이 안 뜸 | 터미널의 오류 메시지를 읽고, 그래도 모르면 선생님 호출 |

## 주의

- **개인정보(이름·연락처·성적 등)를 knowledge.md나 채팅에 넣지 마세요.**
  무료 클라우드 AI는 입력 내용을 학습에 활용할 수 있습니다.
- 배포는 선택 과제입니다. 로컬 실행만으로 발표 가능합니다.

## License

MIT © 2026 Ben Kim
