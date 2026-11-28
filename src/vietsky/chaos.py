"""Gây lỗi có chủ đích để diễn tập sự cố. Bật bằng biến môi trường, ví dụ:
VIETSKY_CHAOS=api_500,null_province python pipelines/run_pipeline.py --source weather
"""
import datetime
import os

FAULTS = {"api_500", "rename_field", "null_province", "swap_latlon", "tz_shift"}
NULL_PROVINCE = "01"
RENAMED_FIELDS = {"pm2_5": "pm25", "temperature_2m": "temp_2m"}


def active(fault: str) -> bool:
    return fault in os.environ.get("VIETSKY_CHAOS", "").split(",")


def http_status(real_status: int) -> int:
    return 500 if active("api_500") else real_status


def break_payload(data: dict, province_code: str) -> dict:
    hourly = data["hourly"]
    if active("rename_field"):
        for old, new in RENAMED_FIELDS.items():
            if old in hourly:
                hourly[new] = hourly.pop(old)
    if active("null_province") and province_code == NULL_PROVINCE:
        for key in hourly:
            if key != "time":
                hourly[key] = [None] * len(hourly[key])
    return data


def swap_latlon(provinces: list[dict], count: int = 3) -> list[dict]:
    if not active("swap_latlon"):
        return provinces
    swapped = [dict(p) for p in provinces]
    for p in swapped[:count]:
        p["lat"], p["lon"] = p["lon"], p["lat"]
    return swapped


def shift_tz(rows: list[tuple]) -> list[tuple]:
    if not active("tz_shift"):
        return rows
    return [(loc, ts.replace(tzinfo=datetime.timezone.utc), *rest) for loc, ts, *rest in rows]
