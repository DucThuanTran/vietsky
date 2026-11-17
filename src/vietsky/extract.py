import requests
import json
import datetime
from typing import Dict, Any
from pathlib import Path

BASE_URL = "https://api.open-meteo.com/v1/forecast"

def fetch_weather(lat: float, lon: float, start_date: str, end_date: str) -> Dict[str, Any]:
    """
        Lấy dữ liệu thời tiết theo giờ từ Open-Meteo API.

        Args:
            lat (float): Vĩ độ của khu vực (Ví dụ: 10.7769)
            lon (float): Kinh độ của khu vực (Ví dụ: 10.6709)
            start_date (str): Ngày bắt đầu lấy dữ liệu (Định dạng: 'YYYY-MM-DD')
            end_date (str): Ngày kết thúc lấy dữ liệu (Định dạng: 'YYYY-MM-DD')

        Returns:
            Dict[str, Any]: Dữ liệu JSON trả về từ API dưới dạng dictionary.
        """
    params = {
        "latitude": lat,
        "longitude": lon,
        "hourly": "temperature_2m,relative_humidity_2m,precipitation,wind_speed_10m",
        "timezone": "Asia/Ho_Chi_Minh",
        "start_date": start_date,
        "end_date": end_date
    }
    response = requests.get(BASE_URL, params=params, timeout=30)

    response.raise_for_status()

    return response.json()

def save_raw(data: Dict[str, Any], city: str, run_date: str) -> Path:
    """
        Lưu dữ liệu JSON thô vào đường dẫn cấu trúc theo ngày và thành phố.

        Args:
            data (Dict[str, Any]): Dữ liệu JSON cần lưu.
            city (str): Tên thành phố.
            run_date (str): Ngày chạy (định dạng: 'YYYY-MM-DD').

        Returns:
            Path: Đường dẫn tới file đã được lưu thành công.
        """
    file_path = Path(f"data/raw/weather/date={run_date}/{city}.json")

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

    saved_path = save_raw(weather_data, CITY, run_date = RUN_DATE)
    print(f"Đã lưu dữ liệu thành công tại: {saved_path}")
