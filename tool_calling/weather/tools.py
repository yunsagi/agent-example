
"""
Claude에게 보여줄 도구 명세 (JSON schema).

[description이 중요한 이유]
- 모델은 도구의 코드를 보지 못한다. name / description / input_schema만 보고
  "이 도구를 쓸지", "어떤 인자를 넣을지"를 결정한다.
- 그래서 description은 tool calling 품질을 좌우하는 가장 큰 요소다.
  가장 흔한 실패는 너무 짧게 쓰는 것(under-description)이다.
- description과 실제 동작이 다르면, 프롬프트를 아무리 고쳐도 모델이 계속 잘못된 방향으로 간다.

[해야 하는 것] - "도구 설명서(man page)"처럼 쓴다. 짧게보다 정확하게. (3~4문장 이상)
1. 무엇을 하는가: 실제 동작과 정확히 일치하게
2. 언제 쓰는가 / 언제 쓰지 않는가: 비슷한 도구와의 경계 (예: 현재 날씨 vs 예보)
3. 무엇을 반환하는가: 그리고 무엇은 반환하지 않는가
4. 한계·주의사항: 지원 범위, 에러가 나는 경우, 그때 모델이 어떻게 하면 되는지
5. 파라미터마다 description: 형식·예시값. 정해진 값이면 enum 사용
6. strict: True + additionalProperties: False 로 스키마에 맞는 인자만 받기

[하지 말아야 하는 것]
- "CRITICAL: You MUST ALWAYS use this tool" 같은 강한 지시
  -> 요즘 모델은 지시를 그대로 따르기 때문에 필요 없는 상황에서도 호출한다 (over-triggering)
- description 안에 예시 대화 / 호출 예시 넣기
  -> 예시와 비슷한 상황에만 갇히고, 요청마다 토큰이 든다. 대신 파라미터 이름·enum을 명확히
- 절차·대화 방식 지시 ("호출 후 항상 ~라고 말해라")
  -> description은 기능에 대한 계약이다. 흐름 제어는 코드나 system prompt에서
"""
tools = [
    {
        "name": "get_current_weather",
        "description": (
            "Returns the current weather conditions for one city: temperature, "
            "feels-like temperature, weather condition (e.g. clear, rain, snow), "
            "humidity (%), and wind speed (m/s). "
            "Use this when the user asks what the weather is like right now or today. "
            "It does not return forecasts or past weather; for future dates use get_forecast. "
            "Data is updated about every 10 minutes, so it may lag slightly behind real conditions. "
            "If the city is not found, it returns an error with code CITY_NOT_FOUND; "
            "in that case ask the user to confirm the city name instead of guessing another one."
        ),
        # 서울과 부산의 날씨를 비교해줘. 라고 사용자가 요청한다면?
        # 스키마 상에서는 string = "Seoul, Busan" 찾다가 CITY_NOT_FOUND 발생할 수도 있음.
        # 그래서 금지만 하지말고 대안도 준비할것.
        "input_schema": {
            "type": "object",
            "properties": {
                "city": {
                    "type": "string",
                    "description": (
                        "City name in English, e.g. 'Seoul', 'Busan', 'Tokyo'. "
                        "One city per call; to compare cities, call the tool once per city."
                    ),
                },
                "unit": {
                    "type": "string",
                    "enum": ["celsius", "fahrenheit"],
                    "description": "Temperature unit. Use celsius unless the user asks otherwise.",
                },
            },
            "required": ["city", "unit"],
            "additionalProperties": False,
        },
        "strict": True,
    },
]