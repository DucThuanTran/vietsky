import pandas as pd
import plotly.express as px
import streamlit as st

from vietsky.load import get_conn

st.set_page_config(page_title="VietSky", page_icon="🌏", layout="wide")


@st.cache_data(ttl="10m")
def query(sql: str, params: tuple = ()) -> pd.DataFrame:
    with get_conn() as conn:
        cur = conn.execute(sql, params)
        cols = [c.name for c in cur.description]
        return pd.DataFrame(cur.fetchall(), columns=cols)


PROVINCE_PM25_30D = """
SELECT l.name, l.region, l.lat, l.lon,
       ROUND(AVG(f.pm2_5)::NUMERIC, 1)::FLOAT AS pm25,
       ROUND(MAX(f.pm2_5)::NUMERIC, 1)::FLOAT AS pm25_max
FROM mart.fact_air_quality_hourly f
JOIN mart.dim_location l ON f.location_key = l.location_key
WHERE f.ts_utc >= NOW() - INTERVAL '30 days' AND f.ts_utc <= NOW()
GROUP BY l.name, l.region, l.lat, l.lon
ORDER BY pm25 DESC
"""

MONTHLY_PM25 = """
SELECT l.name, DATE_TRUNC('month', d.full_date)::DATE AS month_start,
       ROUND(AVG(f.pm2_5)::NUMERIC, 1)::FLOAT AS pm25
FROM mart.fact_air_quality_hourly f
JOIN mart.dim_location l ON f.location_key = l.location_key
JOIN mart.dim_date d ON f.date_key = d.date_key
WHERE l.name = ANY(%s)
GROUP BY l.name, month_start
ORDER BY month_start
"""

HOUR_MONTH_PM25 = """
SELECT d.month, f.hour_vn, ROUND(AVG(f.pm2_5)::NUMERIC, 1)::FLOAT AS pm25
FROM mart.fact_air_quality_hourly f
JOIN mart.dim_location l ON f.location_key = l.location_key
JOIN mart.dim_date d ON f.date_key = d.date_key
WHERE l.name = %s
GROUP BY d.month, f.hour_vn
"""

DAILY_WEATHER_PM25 = """
SELECT a.date_key,
       AVG(a.pm2_5)::FLOAT AS pm25,
       SUM(w.precipitation)::FLOAT AS rain_mm,
       AVG(w.wind_speed)::FLOAT AS wind_kmh
FROM mart.fact_air_quality_hourly a
JOIN mart.fact_weather_hourly w
  ON a.location_key = w.location_key AND a.ts_utc = w.ts_utc
JOIN mart.dim_location l ON a.location_key = l.location_key
WHERE l.name = %s
GROUP BY a.date_key
"""

LOCATION_NAMES = "SELECT name FROM mart.dim_location ORDER BY name"


def sky_page() -> None:
    st.title("🌏 Vietnam Sky")
    st.caption("Hourly PM2.5 (µg/m³) for 34 provinces of Vietnam, from Open-Meteo.")

    ranking = query(PROVINCE_PM25_30D)
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Provinces", len(ranking))
    k2.metric("30-day avg PM2.5", f"{ranking['pm25'].mean():.1f}")
    worst, best = ranking.iloc[0], ranking.iloc[-1]
    k3.metric(f"Most polluted · {worst['pm25']} µg/m³", worst["name"])
    k4.metric(f"Cleanest · {best['pm25']} µg/m³", best["name"])

    left, right = st.columns([3, 2])
    with left:
        st.subheader("30-day average PM2.5 map")
        fig = px.scatter_map(
            ranking, lat="lat", lon="lon", color="pm25", size="pm25", hover_name="name",
            color_continuous_scale="YlOrRd", size_max=22, zoom=4.4,
            center={"lat": 16.0, "lon": 106.5}, map_style="carto-positron", height=620,
        )
        st.plotly_chart(fig, width="stretch")
    with right:
        st.subheader("Province ranking (30 days)")
        st.dataframe(ranking[["name", "region", "pm25", "pm25_max"]], height=620, hide_index=True)

    names = query(LOCATION_NAMES)["name"].tolist()
    picked = st.multiselect("Provinces to compare", names, default=["Hà Nội", "Hồ Chí Minh"])
    if picked:
        trend = query(MONTHLY_PM25, (picked,))
        st.subheader("Monthly PM2.5 trend")
        st.plotly_chart(px.line(trend, x="month_start", y="pm25", color="name", markers=True,
                                color_discrete_sequence=px.colors.qualitative.Set1), width="stretch")

    province = st.selectbox("Province for heatmap and scatter", names, index=names.index("Hà Nội"))
    left, right = st.columns(2)
    with left:
        st.subheader(f"PM2.5 by hour × month · {province}")
        hm = query(HOUR_MONTH_PM25, (province,)).pivot(index="month", columns="hour_vn", values="pm25")
        fig = px.imshow(hm, color_continuous_scale="YlOrRd", aspect="auto",
                        labels={"x": "Hour (Vietnam time)", "y": "Month", "color": "PM2.5"})
        st.plotly_chart(fig, width="stretch")
    with right:
        daily = query(DAILY_WEATHER_PM25, (province,))
        axis = st.radio("Weather factor", ["rain_mm", "wind_kmh"], horizontal=True,
                        format_func={"rain_mm": "Daily rainfall (mm)", "wind_kmh": "Avg wind speed (km/h)"}.get)
        st.subheader(f"Daily PM2.5 vs weather · {province}")
        fig = px.scatter(daily, x=axis, y="pm25", opacity=0.4)
        st.plotly_chart(fig, width="stretch")


RECENT_RUNS = """
SELECT run_id::TEXT, MIN(run_date) AS run_date, MIN(started_at) AS started_at,
       ROUND(EXTRACT(EPOCH FROM MAX(finished_at) - MIN(started_at)))::INT AS seconds,
       COUNT(*) AS stages,
       COUNT(*) FILTER (WHERE status = 'FAILED') AS failed,
       CASE WHEN BOOL_OR(status = 'FAILED') THEN 'FAILED'
            WHEN BOOL_OR(status = 'RUNNING') THEN 'RUNNING' ELSE 'SUCCESS' END AS status
FROM ops.pipeline_runs
GROUP BY run_id
ORDER BY started_at DESC
LIMIT 15
"""

STAGE_ROWS = """
SELECT source, stage, status, rows_in, rows_out, error_message
FROM ops.pipeline_runs
WHERE run_id = %s::UUID
ORDER BY source, started_at
"""

DQ_DAILY = """
SELECT run_date, source,
       ROUND(100.0 * COUNT(*) FILTER (WHERE status = 'PASS') / COUNT(*), 1)::FLOAT AS pass_rate
FROM ops.dq_results
GROUP BY run_date, source
ORDER BY run_date
"""

DQ_FAILS = """
SELECT checked_at, run_date, source, check_name, severity, failed_rows
FROM ops.dq_results
WHERE status = 'FAIL'
ORDER BY checked_at DESC
LIMIT 20
"""

FRESHNESS = """
SELECT 'weather' AS source, MAX(loaded_at) AS last_loaded FROM stg_weather_hourly
UNION ALL
SELECT 'air_quality', MAX(loaded_at) FROM stg_air_quality_hourly
"""

STAGE_ORDER = ["extract", "load", "quality_check", "build_mart", "reconcile"]


def ops_page() -> None:
    st.title("🛠️ Operations")
    st.caption("Did the pipeline run, which stage failed, is the data complete and fresh?")

    fresh = query(FRESHNESS)
    now = pd.Timestamp.now(tz="UTC")
    cols = st.columns(len(fresh) + 1)
    for col, row in zip(cols, fresh.itertuples()):
        hours = (now - row.last_loaded).total_seconds() / 3600
        status = "✅ within 24h SLA" if hours <= 24 else "🔴 breached 24h SLA"
        col.metric(f"Freshness · {row.source} · {status}", f"{hours:.1f} h ago")

    runs = query(RECENT_RUNS)
    cols[-1].metric(f"Latest run · {runs.iloc[0]['seconds'] or 0}s", runs.iloc[0]["status"])

    st.subheader("Recent runs")
    st.dataframe(runs, hide_index=True)

    run_id = st.selectbox("Run details", runs["run_id"])
    stages = query(STAGE_ROWS, (run_id,))
    left, right = st.columns(2)
    with left:
        st.subheader("Rows per stage")
        funnel = stages[stages["stage"].isin(["extract", "load"])].copy()
        funnel["stage"] = pd.Categorical(funnel["stage"], STAGE_ORDER, ordered=True)
        fig = px.bar(funnel.sort_values("stage"), x="stage", y="rows_out", color="source",
                     barmode="group", text="rows_out")
        st.plotly_chart(fig, width="stretch")
    with right:
        st.subheader("Stage status")
        st.dataframe(stages, hide_index=True)

    st.subheader("Data quality pass rate by day")
    dq = query(DQ_DAILY)
    if dq.empty:
        st.info("No quality results yet.")
    else:
        fig = px.bar(dq, x="run_date", y="pass_rate", color="source", barmode="group", range_y=[0, 105])
        st.plotly_chart(fig, width="stretch")

    st.subheader("Recent failed checks")
    st.dataframe(query(DQ_FAILS), hide_index=True)


st.navigation([
    st.Page(sky_page, title="Vietnam Sky", icon="🌏", default=True),
    st.Page(ops_page, title="Operations", icon="🛠️"),
]).run()
