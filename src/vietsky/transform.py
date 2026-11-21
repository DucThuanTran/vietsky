from datetime import datetime, timezone, timedelta

def to_rows(data: dict, location_id: str, json_cols:list) -> list:
    hourly = data['hourly']
    tz = timezone(timedelta(seconds=data['utc_offset_seconds']))
    times = hourly['time']

    for c in json_cols:
        if len(hourly[c]) != len(times):
            raise ValueError(f"{c}: {len(hourly[c])} values, expected {len(times)}")

    rows = []
    for i, t in enumerate(times):
        ts = datetime.fromisoformat(t).replace(tzinfo=tz)
        values = [hourly[c][i] for c in json_cols]
        rows.append((location_id, ts, *values))

    return rows
