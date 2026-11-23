import requests
import json
import datetime
import time
from typing import Dict, Any
from pathlib import Path

WEATHER_URL = "https://api.open-meteo.com/v1/forecast"
AIR_QUALITY_URL = "https://air-quality-api.open-meteo.com/v1/air-quality"

def fetch_hourly(lat: float, lon: float, variables:str , start_date: str, end_date: str, url:str) -> Dict[str, Any]:
    params = {
        "latitude": lat,
        "longitude": lon,
        "hourly": variables,
        "timezone": "Asia/Ho_Chi_Minh",
        "start_date": start_date,
        "end_date": end_date
    }
    for attempt in range(1, 5):
        try:
            response = requests.get(url, params=params, timeout=30)
            if response.status_code in {429, 500, 502, 503, 504}:
                error = f"HTTP {response.status_code}"
            else:
                response.raise_for_status()
                return response.json()
        except (requests.Timeout, requests.ConnectionError) as e:
            error = e
        if attempt == 4:
            raise RuntimeError(f"{url} failed after 4 attempts: {error}")
        wait = 2 ** attempt
        print(f"Retry {attempt}/4 after {wait}s: {error}")
        time.sleep(wait)

def fetch_weather(lat: float, lon: float, start_date: str, end_date: str) -> Dict[str, Any]:
    return fetch_hourly(lat, lon, "temperature_2m,relative_humidity_2m,precipitation,wind_speed_10m", start_date, end_date, url=WEATHER_URL)


def fetch_air_quality(lat: float, lon: float, start_date: str, end_date: str) -> Dict[str, Any]:
    return fetch_hourly(lat, lon, "pm2_5,pm10,us_aqi,nitrogen_dioxide,ozone", start_date, end_date, url=AIR_QUALITY_URL)

def save_raw(data: Dict[str, Any], city: str, run_date: str, source: str) -> Path:
    file_path = Path(f"data/raw/{source}/date={run_date}/{city}.json")

    file_path.parent.mkdir(parents=True, exist_ok=True)

    file_path.write_text(
        json.dumps(data, indent=4),
        encoding="utf-8"
    )

    return file_path

if __name__ == "__main__":
    LAT = 10.762622
    LON = 106.660172
    START_DATE = "2026-11-01"
    END_DATE = "2026-11-07"
    RUN_DATE = datetime.datetime.now().strftime("%Y-%m-%d")
    CITY = "hcm"

    print(f"Đang gọi API lấy thời tiết cho {CITY} từ {START_DATE} đến {END_DATE}...")

    weather_data = fetch_weather(LAT, LON, START_DATE, END_DATE)
    print(f"Đã nhận {len(weather_data['hourly']['time'])} dòng dữ liệu theo giờ")

    air_quality_data = fetch_air_quality(LAT, LON, START_DATE, END_DATE)
    print(f"Đã nhận {len(air_quality_data['hourly']['time'])} dòng dữ liệu theo giờ")

    saved_weather_path = save_raw(weather_data, CITY, run_date = RUN_DATE, source="weather")
    print(f"Đã lưu dữ liệu thành công tại: {saved_weather_path}")

    saved_air_quality_path = save_raw(air_quality_data, CITY, run_date=RUN_DATE, source='air_quality')
    print(f"Đã lưu dữ liệu thành công tại: {saved_air_quality_path}")
