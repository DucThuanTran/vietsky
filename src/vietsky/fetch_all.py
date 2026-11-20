import datetime
import logging
import sys
import time
from pathlib import Path

from extract import fetch_weather, fetch_air_quality, save_raw
from validate import load_provinces, check_row_counts, check_unique_names, check_coordinates

logger = logging.getLogger(__name__)

PROVINCES_PATH = "config/provinces.csv"
DAYS_BACK = 7
EXPECTED_ROWS = (DAYS_BACK + 1) * 24


def setup_logging():
    Path("logs").mkdir(exist_ok=True)
    logging.basicConfig(
        filename="logs/fetch_all.log",
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s"
    )


def main():
    setup_logging()
    rows = load_provinces(PROVINCES_PATH)
    errors = []
    errors.extend(check_row_counts(rows))
    errors.extend(check_unique_names(rows))
    errors.extend(check_coordinates(rows))

    if errors:
        for error in errors:
            logger.error("Validate thất bại: %s", error)
        sys.exit(1)

    today = datetime.date.today()
    run_date = today.isoformat()
    end = today.isoformat()
    start = (today - datetime.timedelta(days=DAYS_BACK)).isoformat()
    logger.info("Bắt đầu: %d tỉnh, dữ liệu %s → %s, run_date=%s", len(rows), start, end, run_date)

    ok = 0
    failed = []
    for row in rows:
        name = row["name"]
        try:
            lat, lon = float(row["lat"]), float(row["lon"])
            results = {
                "weather": fetch_weather(lat, lon, start, end),
                "air_quality": fetch_air_quality(lat, lon, start, end),
            }
            for source, data in results.items():
                n = len(data["hourly"]["time"])
                path = save_raw(data, row["province_code"], run_date, source=source)
                logger.info("%s [%s]: %d dòng → %s", name, source, n, path)
                if n != EXPECTED_ROWS:
                    logger.warning("%s [%s]: nhận %d dòng, kỳ vọng %d", name, source, n, EXPECTED_ROWS)
            ok += 1
        except Exception as e:
            logger.error("%s: %s", name, e)
            failed.append(name)
        time.sleep(1)

    logger.info("Hoàn tất: %d OK, %d lỗi: %s", ok, len(failed), failed)
    if failed:
        sys.exit(1)


if __name__ == "__main__":
    main()
