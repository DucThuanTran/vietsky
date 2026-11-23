import datetime
import os
from dataclasses import dataclass
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()
RAW_DIR = Path("data/raw")
PROVINCES_PATH = Path("config/provinces.csv")
DAYS_BACK = 7
EXPECTED_ROWS = (DAYS_BACK + 1) * 24
TIMEZONE = "Asia/Ho_Chi_Minh"
WEATHER_URL = "https://api.open-meteo.com/v1/forecast"
AIR_QUALITY_URL = "https://air-quality-api.open-meteo.com/v1/air-quality"
ARCHIVE_URL = "https://archive-api.open-meteo.com/v1/archive"

@dataclass(frozen=True)
class Source:
    name: str
    url: str
    table: str
    columns: dict
    history_url: str
    history_start: datetime.date

    @property
    def api_variables(self) -> str:
        return ",".join(self.columns.keys())

SOURCES = [
    Source(
        name="weather",
        url=WEATHER_URL,
        table="stg_weather_hourly",
        history_url=ARCHIVE_URL,
        history_start=datetime.date(1940, 1, 1),
        columns={
            "temperature_2m": "temperature",
            "relative_humidity_2m": "humidity",
            "precipitation": "precipitation",
            "wind_speed_10m": "wind_speed"
        }
    ),
    Source(
        name="air_quality",
        url=AIR_QUALITY_URL,
        table="stg_air_quality_hourly",
        history_url=AIR_QUALITY_URL,
        history_start=datetime.date(2022, 8, 4),
        columns={
            "pm2_5":"pm2_5",
            "pm10":"pm10",
            "us_aqi":"us_aqi",
            "nitrogen_dioxide":"nitrogen_dioxide",
            "ozone":"ozone"
        }
    )
]

def db_conninfo() -> dict:
    return {
        "host": "localhost",
        "port": 5433,
        "dbname": os.environ["POSTGRES_DB"],
        "user": os.environ["POSTGRES_USER"],
        "password": os.environ["POSTGRES_PASSWORD"]
    }
