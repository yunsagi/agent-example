"""
실제로 실행되는 도구 함수 + 이름→함수 매핑.

[핵심] handler는 tools.py의 description에 적은 "계약"을 그대로 지켜야 한다.
- description에 약속한 필드를 그대로 반환한다 (temperature, feels_like, condition, humidity, wind_speed)
- description에 약속한 에러 코드를 그대로 쓴다 (CITY_NOT_FOUND)
- description과 동작이 다르면 프롬프트로는 고칠 수 없다

[에러 처리]
- 에러는 예외로 터뜨리지 않고 dict로 돌려준다 -> main.py에서 tool_result에 is_error=True를 붙여 모델에게 전달
- 그래야 모델이 실패를 알고, description에 적은 대로 사용자에게 도시 이름을 다시 묻는다
"""

# 가짜 데이터 (나중에 실제 날씨 API로 교체)
FAKE_WEATHER = {
    "Seoul": {"temperature": 3.0, "feels_like": -1.0, "condition": "clear", "humidity": 45, "wind_speed": 2.5},
    "Busan": {"temperature": 8.0, "feels_like": 6.0, "condition": "cloudy", "humidity": 60, "wind_speed": 4.1},
}


def get_current_weather(city: str, unit: str) -> dict:
    # city: 도시 하나만 받는다 ("One city per call" 계약)
    data = FAKE_WEATHER.get(city)
    if data is None:
        # description에 약속한 에러 코드 그대로
        return {"error": "CITY_NOT_FOUND", "message": f"City '{city}' was not found."}

    result = dict(data)  # 원본 FAKE_WEATHER가 바뀌지 않도록 복사
    # unit: strict + enum 이라 "celsius" / "fahrenheit" 외의 값은 들어오지 않는다
    if unit == "fahrenheit":
        result["temperature"] = round(result["temperature"] * 9 / 5 + 32, 1)
        result["feels_like"] = round(result["feels_like"] * 9 / 5 + 32, 1)

    return {"city": city, "unit": unit, **result}


# tool_use 블록의 name -> 실행할 함수
# 사용: HANDLERS[block.name](**block.input)
# tools.py의 "name"과 키가 정확히 같아야 한다
HANDLERS = {
    "get_current_weather": get_current_weather,
}
