"""
실제로 실행되는 도구 함수 + 이름→함수 매핑.

[핵심] handler는 tools.py의 description에 적은 "계약"을 그대로 지켜야 한다.
- description에 약속한 필드를 그대로 반환한다
  - get_current_weather: temperature, feels_like, condition, humidity, wind_speed
  - get_forecast: date, min, max, condition, precipitation_chance
- description에 약속한 에러 코드를 그대로 쓴다 (CITY_NOT_FOUND, RANGE_EXCEEDED)
- description과 동작이 다르면 프롬프트로는 고칠 수 없다

[에러 처리]
- 에러는 예외로 터뜨리지 않고 dict로 돌려준다 -> main.py에서 tool_result에 is_error=True를 붙여 모델에게 전달
- 그래야 모델이 실패를 알고, description에 적은 대로 사용자에게 도시 이름을 다시 묻는다

[도구 추가 방법]
1. tools.py에 명세 추가
2. 여기에 함수 작성
3. HANDLERS에 등록
-> main.py는 HANDLERS[block.name]으로 함수를 찾기 때문에 수정할 필요 없음
"""

from datetime import date, timedelta

# 가짜 데이터 (나중에 실제 날씨 API로 교체)
FAKE_WEATHER = {
    "Seoul": {"temperature": 3.0, "feels_like": -1.0, "condition": "clear", "humidity": 45, "wind_speed": 2.5},
    "Busan": {"temperature": 8.0, "feels_like": 6.0, "condition": "cloudy", "humidity": 60, "wind_speed": 4.1},
}

# 내일부터 7일치 예보 (리스트의 0번 = 내일)
FAKE_FORECAST = {
    "Seoul": [
        {"min": -2.0, "max": 5.0, "condition": "clear", "precipitation_chance": 10},
        {"min": 0.0, "max": 7.0, "condition": "cloudy", "precipitation_chance": 30},
        {"min": 1.0, "max": 6.0, "condition": "rain", "precipitation_chance": 80},
        {"min": -3.0, "max": 2.0, "condition": "snow", "precipitation_chance": 70},
        {"min": -5.0, "max": 1.0, "condition": "clear", "precipitation_chance": 0},
        {"min": -4.0, "max": 3.0, "condition": "clear", "precipitation_chance": 5},
        {"min": -1.0, "max": 6.0, "condition": "cloudy", "precipitation_chance": 20},
    ],
    "Busan": [
        {"min": 4.0, "max": 11.0, "condition": "cloudy", "precipitation_chance": 20},
        {"min": 5.0, "max": 12.0, "condition": "rain", "precipitation_chance": 90},
        {"min": 6.0, "max": 10.0, "condition": "rain", "precipitation_chance": 60},
        {"min": 3.0, "max": 9.0, "condition": "clear", "precipitation_chance": 10},
        {"min": 2.0, "max": 8.0, "condition": "clear", "precipitation_chance": 0},
        {"min": 3.0, "max": 10.0, "condition": "cloudy", "precipitation_chance": 30},
        {"min": 5.0, "max": 12.0, "condition": "clear", "precipitation_chance": 10},
    ],
}


def to_fahrenheit(celsius: float) -> float:
    return round(celsius * 9 / 5 + 32, 1)


def get_current_weather(city: str, unit: str) -> dict:
    # city: 도시 하나만 받는다 ("One city per call" 계약)
    data = FAKE_WEATHER.get(city)
    if data is None:
        # description에 약속한 에러 코드 그대로
        return {"error": "CITY_NOT_FOUND", "message": f"City '{city}' was not found."}

    result = dict(data)  # 원본 FAKE_WEATHER가 바뀌지 않도록 복사
    # unit: strict + enum 이라 "celsius" / "fahrenheit" 외의 값은 들어오지 않는다
    if unit == "fahrenheit":
        result["temperature"] = to_fahrenheit(result["temperature"])
        result["feels_like"] = to_fahrenheit(result["feels_like"])

    return {"city": city, "unit": unit, **result}


def get_forecast(city: str, days: int, unit: str) -> dict:
    data = FAKE_FORECAST.get(city)
    if data is None:
        return {"error": "CITY_NOT_FOUND", "message": f"City '{city}' was not found."}

    # 스키마의 integer 타입만으로는 1~7 범위가 보장되지 않으니 직접 검증
    if not 1 <= days <= 7:
        return {"error": "RANGE_EXCEEDED", "message": f"days must be between 1 and 7, got {days}."}

    today = date.today()
    forecast = []
    for i, day in enumerate(data[:days], start=1):  # i=1 -> 내일
        # 날짜를 넣어줘야 모델이 "이번 주말"이 며칠인지 계산할 수 있다
        item = {"date": (today + timedelta(days=i)).isoformat(), **day}
        if unit == "fahrenheit":
            item["min"] = to_fahrenheit(item["min"])
            item["max"] = to_fahrenheit(item["max"])
        forecast.append(item)

    return {"city": city, "unit": unit, "forecast": forecast}


# tool_use 블록의 name -> 실행할 함수
# 사용: HANDLERS[block.name](**block.input)
# tools.py의 "name"과 키가 정확히 같아야 한다
HANDLERS = {
    "get_current_weather": get_current_weather,
    "get_forecast": get_forecast,
}
