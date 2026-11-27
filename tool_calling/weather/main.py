
import json

import anthropic
from config import MODEL
from weather.handlers import HANDLERS
from weather.tools import tools

client = anthropic.Anthropic()

MAX_TURNS = 10

def run_tool(block) -> dict:
    """tool_use 블록 하나를 실행해서 tool_result 블록으로 만든다."""
    handler = HANDLERS.get(block.name)
    if handler is None:
        result = {"error": "UNKNOWN_TOOL", "message": f"Tool '{block.name}' does not exist."}
    else:
        try:
            result = handler(**block.input)  # {"city": "Seoul", "unit": "celsius"} -> 키워드 인자로 펼침
        except Exception as e:
            # handler에서 예외가 나도 루프를 죽이지 않고 모델에게 알려준다
            result = {"error": "TOOL_EXCEPTION", "message": str(e)}

    return {
        "type": "tool_result",
        "tool_use_id": block.id,  # 어떤 tool_use에 대한 결과인지 짝을 맞춤 (필수)
        "content": json.dumps(result, ensure_ascii=False),
        "is_error": "error" in result,
    }

def run(user_input: str) -> str:
    messages = [{"role": "user", "content": user_input}]

    for turn in range(1, MAX_TURNS + 1):
        response = client.beta.messages.create(
            model=MODEL,
            max_tokens=16000,
            tools=tools,
            messages=messages,
            # 안전 분류기가 요청을 거절하면 서버가 다른 모델로 자동 재시도 (선택 사항, 지워도 루프는 동작)
            betas=["server-side-fallback-2026-07-01"],
            fallbacks="default",
        )
        print(f"[turn {turn}] stop_reason={response.stop_reason}")

        # 응답 전체를 그대로 추가한다. tool_use 블록만 골라 넣으면 안 됨
        # (thinking 블록 등도 같이 돌려보내야 다음 요청이 정상 동작)
        messages.append({"role": "assistant", "content": response.content})

        if response.stop_reason == "tool_use":
            tool_results = []
            for block in response.content:
                if block.type == "tool_use":
                    print(f"  -> {block.name}({block.input})")
                    tool_results.append(run_tool(block))
                    print(f"  <- {tool_results[-1]['content']}")

            # 병렬 호출이면 결과 여러 개를 "한 user 메시지"에 모아서 보낸다
            messages.append({"role": "user", "content": tool_results})
            continue

        if response.stop_reason == "refusal":
            return "[요청이 거절되었습니다]"

        if response.stop_reason == "max_tokens":
            return "[max_tokens에 도달해 응답이 잘렸습니다]"

        # end_turn: 최종 답변
        return "".join(b.text for b in response.content if b.type == "text")

    return f"[MAX_TURNS({MAX_TURNS}) 초과]"


if __name__ == "__main__":
    print(run("대구 날씨 어때?"))