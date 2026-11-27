# agent-example

LLM 에이전트를 공부하면서 **직접 코드를 짜보며** 정리하는 예제 저장소입니다.
주제마다 독립된 uv 프로젝트로 나누어 진행합니다.

## 구조

```
agent-example/
└── tool_calling/          # Tool calling & 에이전트 루프
    ├── pyproject.toml
    ├── config.py          # .env 로드, 모델 설정
    └── weather/
        ├── tools.py       # 도구 명세 (name, description, input_schema)
        ├── handlers.py    # 도구의 실제 구현 + 이름→함수 매핑
        └── main.py        # 에이전트 루프
```

## tool_calling

SDK 헬퍼 없이 tool calling 흐름을 직접 구현하며 공부합니다.

- **tools.py** — 모델이 보는 도구 명세. description을 어떻게 쓰느냐에 따라 호출 품질이 달라지는 걸 실험
- **handlers.py** — 실제로 실행되는 함수. 명세에 적은 계약(반환 필드, 에러 코드)을 그대로 지킴
- **main.py** — `tool_use` → 실행 → `tool_result`를 반복하는 루프. 병렬 호출과 에러 전달(`is_error`) 처리

### 실행

```bash
cd tool_calling
cp .env.example .env   # ANTHROPIC_API_KEY 입력
uv sync
uv run python -m weather.main
```
