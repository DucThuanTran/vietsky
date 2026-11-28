import datetime

from vietsky.quality import check_window, make_result, rules_for


def test_make_result_pass_when_within_threshold():
    assert make_result("x", "CRITICAL", 0, 0)["status"] == "PASS"


def test_make_result_fail_when_over_threshold():
    assert make_result("x", "CRITICAL", 3, 0)["status"] == "FAIL"


def test_rules_for_keeps_shared_and_own_rules():
    weather = {r["name"] for r in rules_for("weather")}
    air = {r["name"] for r in rules_for("air_quality")}
    assert "pm25_range" not in weather
    assert "pm25_range" in air
    assert "unique_key" in weather and "unique_key" in air


def test_check_window_covers_8_full_vn_days():
    window = check_window(datetime.date(2026, 11, 26))
    assert window["start"].isoformat() == "2026-11-19T00:00:00+07:00"
    assert window["end"].isoformat() == "2026-11-27T00:00:00+07:00"
