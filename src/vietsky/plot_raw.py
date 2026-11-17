import plotly.express as px
import json

def load_raw(path):
    with open(path, mode="r", encoding='utf-8') as f:
        return json.load(f)

def plot_temperature(data, city):
    hourly = data["hourly"]
    times = hourly["time"]
    temperatures = hourly["temperature_2m"]
    unit = data["hourly_units"]["temperature_2m"]

    fig =  px.line(x=times, y=temperatures, title=f"Nhiệt độ theo giờ - {city}")
    fig.update_layout(xaxis_title="Thời gian", yaxis_title=f"Nhiệt độ ({unit})")
    return fig


if __name__ == "__main__":
    data = load_raw("data/raw/weather/date=2026-11-17/hcm.json")
    fig = plot_temperature(data, "HCM")
    fig.show()