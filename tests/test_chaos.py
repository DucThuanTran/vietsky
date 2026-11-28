import datetime

from vietsky import chaos

VN = datetime.timezone(datetime.timedelta(hours=7))


def payload():
    return {"hourly": {"time": ["2026-11-28T00:00"], "pm2_5": [12.0], "pm10": [20.0]}}


def test_no_fault_leaves_payload_untouched(monkeypatch):
    monkeypatch.delenv("VIETSKY_CHAOS", raising=False)
    assert chaos.break_payload(payload(), "01") == payload()


def test_rename_field(monkeypatch):
    monkeypatch.setenv("VIETSKY_CHAOS", "rename_field")
    hourly = chaos.break_payload(payload(), "01")["hourly"]
    assert "pm2_5" not in hourly and hourly["pm25"] == [12.0]


def test_null_province_only_hits_target(monkeypatch):
    monkeypatch.setenv("VIETSKY_CHAOS", "null_province")
    assert chaos.break_payload(payload(), "01")["hourly"]["pm10"] == [None]
    assert chaos.break_payload(payload(), "79")["hourly"]["pm10"] == [20.0]


def test_swap_latlon_does_not_mutate_input(monkeypatch):
    monkeypatch.setenv("VIETSKY_CHAOS", "swap_latlon")
    provinces = [{"lat": "21.0", "lon": "105.8"}]
    swapped = chaos.swap_latlon(provinces)
    assert swapped[0] == {"lat": "105.8", "lon": "21.0"}
    assert provinces[0]["lat"] == "21.0"


def test_tz_shift_moves_time_7_hours_later(monkeypatch):
    monkeypatch.setenv("VIETSKY_CHAOS", "tz_shift")
    ts = datetime.datetime(2026, 11, 28, 8, 0, tzinfo=VN)
    (_, shifted, _), = chaos.shift_tz([("01", ts, 1.0)])
    assert shifted - ts == datetime.timedelta(hours=7)
