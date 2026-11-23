from datetime import datetime, timezone

import pytest

from vietsky.transform import to_rows


@pytest.fixture
def sample_data():
    return {
        "utc_offset_seconds": 25200,
        "hourly": {
            "time": ["2026-11-20T00:00", "2026-11-20T01:00", "2026-11-20T02:00"],
            "temperature_2m": [20.5, None, 21.0],
            "relative_humidity_2m": [80, 82, 85],
        },
    }


def test_row_count(sample_data):
    rows = to_rows(sample_data, "01", ["temperature_2m"])
    assert len(rows) == 3
    assert rows[0][0] == "01"


def test_utc_conversion(sample_data):
    rows = to_rows(sample_data, "01", ["temperature_2m"])
    assert rows[0][1].astimezone(timezone.utc) == datetime(2026, 11, 19, 17, tzinfo=timezone.utc)


def test_none_kept(sample_data):
    rows = to_rows(sample_data, "01", ["temperature_2m"])
    assert rows[1][2] is None


def test_column_order(sample_data):
    rows = to_rows(sample_data, "01", ["temperature_2m", "relative_humidity_2m"])
    assert rows[0][2:] == (20.5, 80)


def test_length_mismatch(sample_data):
    sample_data["hourly"]["temperature_2m"].pop()
    with pytest.raises(ValueError):
        to_rows(sample_data, "01", ["temperature_2m"])
