import json
import time
from typing import Dict, Any
from pathlib import Path

import requests

from vietsky import chaos
from vietsky.config import RAW_DIR

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
            status = chaos.http_status(response.status_code)
            if status in {429, 500, 502, 503, 504}:
                error = f"HTTP {status}"
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

def save_raw(data: Dict[str, Any], city: str, run_date: str, source: str) -> Path:
    file_path = RAW_DIR / source / f"date={run_date}" / f"{city}.json"

    file_path.parent.mkdir(parents=True, exist_ok=True)

    file_path.write_text(
        json.dumps(data, indent=4),
        encoding="utf-8"
    )

    return file_path
