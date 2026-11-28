import csv
import sys

EXPECTED_COUNT = 34
LAT_MIN, LAT_MAX = 8, 24
LON_MIN, LON_MAX = 102, 110

def load_provinces(path: str) -> list:
    with open(path, mode="r", encoding='utf-8') as f:
        return list(csv.DictReader(f))

def check_row_counts(rows: list) -> list:
    errors = []
    actual_count = len(rows)
    if actual_count != EXPECTED_COUNT:
        errors.append(f"Có {actual_count} dòng, cần {EXPECTED_COUNT}")
    return errors

def check_unique_names(rows: list) -> list:
    errors = []
    seen = set()
    for row in rows:
        if row['name'] in seen:
            errors.append(f"Trùng tên: {row['name']}")
        else:
            seen.add(row['name'])
    return errors

def check_coordinates(rows: list) -> list:
    errors = []
    for row in rows:
        name = row['name']
        lat = row['lat']
        lon = row['lon']
        try:
            lat = float(lat)
            lon = float(lon)
        except ValueError:
            errors.append(f"Tọa độ không phải số: {name}")
            continue
        if not (LAT_MIN <= lat <= LAT_MAX) or not (LON_MIN <= lon <= LON_MAX):
            errors.append(f"{name} nằm ngoài Việt Nam: ({lat}, {lon})")
    return errors

def validate_provinces(rows: list) -> list:
    return check_row_counts(rows) + check_unique_names(rows) + check_coordinates(rows)

def main():
    rows = load_provinces("config/provinces.csv")
    errors = validate_provinces(rows)
    if errors:
        print("\n".join(errors))
        sys.exit(1)
    else:
        print("OK: 34 tỉnh hợp lệ")

if __name__ == "__main__":
    main()