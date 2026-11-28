import csv
import logging
import time
from pathlib import Path
import requests

logger = logging.getLogger(__name__)

PROVINCES = [
    # --- North (15) ---
    {"province_code": "01", "name": "Hà Nội",      "search_name": "Hanoi",         "region": "north"},
    {"province_code": "04", "name": "Cao Bằng",    "search_name": "Cao Bang",      "region": "north"},
    {"province_code": "08", "name": "Tuyên Quang", "search_name": "Tuyen Quang",   "region": "north"},
    {"province_code": "11", "name": "Điện Biên",   "search_name": "Dien Bien Phu", "region": "north"},
    {"province_code": "12", "name": "Lai Châu",    "search_name": "Lai Chau",      "region": "north"},
    {"province_code": "14", "name": "Sơn La",      "search_name": "Son La",        "region": "north"},
    {"province_code": "15", "name": "Lào Cai",     "search_name": "Yen Bai",       "region": "north"},
    {"province_code": "19", "name": "Thái Nguyên", "search_name": "Thai Nguyen",   "region": "north"},
    {"province_code": "20", "name": "Lạng Sơn",    "search_name": "Lang Son",      "region": "north"},
    {"province_code": "22", "name": "Quảng Ninh",  "search_name": "Ha Long",       "region": "north"},
    {"province_code": "24", "name": "Bắc Ninh",    "search_name": "Bac Giang",     "region": "north"},
    {"province_code": "25", "name": "Phú Thọ",     "search_name": "Viet Tri",      "region": "north"},
    {"province_code": "31", "name": "Hải Phòng",   "search_name": "Haiphong",      "region": "north"},
    {"province_code": "33", "name": "Hưng Yên",    "search_name": "Hung Yen",      "region": "north"},
    {"province_code": "37", "name": "Ninh Bình",   "search_name": "Ninh Binh",     "region": "north"},
    # --- Central & Central Highlands (11) ---
    {"province_code": "38", "name": "Thanh Hóa",   "search_name": "Thanh Hoa",     "region": "central"},
    {"province_code": "40", "name": "Nghệ An",     "search_name": "Vinh",          "region": "central"},
    {"province_code": "42", "name": "Hà Tĩnh",     "search_name": "Ha Tinh",       "region": "central"},
    {"province_code": "44", "name": "Quảng Trị",   "search_name": "Dong Hoi",      "region": "central"},
    {"province_code": "46", "name": "Huế",         "search_name": "Hue",           "region": "central"},
    {"province_code": "48", "name": "Đà Nẵng",     "search_name": "Da Nang",       "region": "central"},
    {"province_code": "51", "name": "Quảng Ngãi",  "search_name": "Quang Ngai",    "region": "central"},
    {"province_code": "52", "name": "Gia Lai",     "search_name": "Quy Nhon",      "region": "central"},
    {"province_code": "56", "name": "Khánh Hòa",   "search_name": "Nha Trang",     "region": "central"},
    {"province_code": "66", "name": "Đắk Lắk",     "search_name": "Buon Ma Thuot", "region": "central"},
    {"province_code": "68", "name": "Lâm Đồng",    "search_name": "Da Lat",        "region": "central"},
    # --- South (8) ---
    {"province_code": "75", "name": "Đồng Nai",    "search_name": "Bien Hoa",         "region": "south"},
    {"province_code": "79", "name": "Hồ Chí Minh", "search_name": "Ho Chi Minh City", "region": "south"},
    {"province_code": "80", "name": "Tây Ninh",    "search_name": "Tan An",           "region": "south"},
    {"province_code": "82", "name": "Đồng Tháp",   "search_name": "My Tho",           "region": "south"},
    {"province_code": "86", "name": "Vĩnh Long",   "search_name": "Vinh Long",        "region": "south"},
    {"province_code": "91", "name": "An Giang",    "search_name": "Rach Gia",         "region": "south"},
    {"province_code": "92", "name": "Cần Thơ",     "search_name": "Can Tho",          "region": "south"},
    {"province_code": "96", "name": "Cà Mau",      "search_name": "Ca Mau",           "region": "south"},
]

def search_place(name: str) -> list:
    geocoding_api = "https://geocoding-api.open-meteo.com/v1/search"
    params = {
        "name": name,
        "countryCode":"VN",
        "count": 10
    }

    try:
        response = requests.get(geocoding_api, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
    except requests.RequestException as e:
        logger.warning("API call failed for %s: %s", name, e)
        return []
    return data.get("results", [])

def pick_best(results: list) -> dict | None:
    for place in results:
        if place.get("feature_code") == "PPLC":
            return place
    for place in results:
        if place.get("feature_code") == "PPLA":
            return place
    return None

def main():
    rows = []
    for province in PROVINCES:
        time.sleep(1)
        name = province["name"]
        search_name = province["search_name"]
        best = pick_best(search_place(search_name))
        if best is not None:
            lat = best['latitude']
            lon = best['longitude']
            note = ''
            logger.info("%s → %s (%s)", name, best["name"], best["feature_code"])
        else:
            lat = ''
            lon = ''
            note = 'not found'
            logger.warning("Not found: %s (search_name=%s)", name, search_name)
        row = {
            "province_code": province["province_code"],
            "name": name,
            "search_name": search_name,
            "region": province["region"],
            "lat": lat,
            "lon": lon,
            "note": note
        }
        rows.append(row)

    Path("config").mkdir(exist_ok=True)
    with open("config/provinces.csv", "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["province_code", "name", "search_name", "region",
                                               "lat", "lon", "note"])
        writer.writeheader()
        for row in rows:
            writer.writerow(row)

        missing = sum(1 for row in rows if row["lat"] == "")
        logger.info("Wrote %d provinces. Provinces needing manual fix: %d", len(rows), missing)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()