#!/usr/bin/env python3
"""Estimate Hong Kong flying termite swarm risk from HKO open data."""

from __future__ import annotations

import argparse
import csv
import json
import math
import os
import sys
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any
from urllib.error import URLError
from urllib.request import urlopen


HK_TZ = timezone(timedelta(hours=8))

CURRENT_WEATHER_URL = "https://data.weather.gov.hk/weatherAPI/opendata/weather.php?dataType=rhrread&lang=tc"
FORECAST_URL = "https://data.weather.gov.hk/weatherAPI/opendata/weather.php?dataType=flw&lang=tc"
HOURLY_RAIN_URL = "https://data.weather.gov.hk/weatherAPI/opendata/hourlyRainfall.php?lang=tc"
WIND_URL = "https://data.weather.gov.hk/weatherAPI/hko_data/regional-weather/latest_10min_wind.csv"
PRESSURE_URL = "https://data.weather.gov.hk/weatherAPI/hko_data/regional-weather/latest_1min_pressure.csv"

DEFAULT_STATE = Path.home() / ".openclaw" / "state" / "flying-ant-risk-hk" / "history.json"


@dataclass
class Factor:
    name: str
    points: int
    detail: str


def fetch_text(url: str, timeout: int = 15) -> str:
    try:
        with urlopen(url, timeout=timeout) as response:
            return response.read().decode("utf-8-sig")
    except URLError as exc:
        raise RuntimeError(f"failed to fetch {url}: {exc}") from exc


def fetch_json(url: str) -> dict[str, Any]:
    return json.loads(fetch_text(url))


def parse_iso(value: str | None) -> datetime | None:
    if not value:
        return None
    return datetime.fromisoformat(value).astimezone(HK_TZ)


def parse_hko_minute(value: str) -> datetime:
    return datetime.strptime(value, "%Y%m%d%H%M").replace(tzinfo=HK_TZ)


def is_number(value: Any) -> bool:
    try:
        if value in (None, "", "N/A"):
            return False
        float(value)
        return True
    except (TypeError, ValueError):
        return False


def number(value: Any) -> float | None:
    return float(value) if is_number(value) else None


def select_by_name(rows: list[dict[str, Any]], key: str, preferred: str | None) -> dict[str, Any] | None:
    if preferred:
        for row in rows:
            if str(row.get(key, "")).casefold() == preferred.casefold():
                return row
        for row in rows:
            if preferred.casefold() in str(row.get(key, "")).casefold():
                return row
    return None


def parse_csv_rows(text: str) -> list[dict[str, str]]:
    return list(csv.DictReader(text.splitlines()))


def load_history(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return []
    return data if isinstance(data, list) else []


def save_history(path: Path, history: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    cutoff = datetime.now(HK_TZ) - timedelta(days=4)
    compact = []
    for item in history:
        observed_at = parse_iso(item.get("observed_at"))
        if observed_at and observed_at >= cutoff:
            compact.append(item)
    path.write_text(json.dumps(compact[-1000:], ensure_ascii=False, indent=2), encoding="utf-8")


def max_rain_between(
    history: list[dict[str, Any]],
    now: datetime,
    newer_than_hours: int,
    older_than_hours: int = 0,
) -> float | None:
    cutoff = now - timedelta(hours=newer_than_hours)
    upper = now - timedelta(hours=older_than_hours)
    values = []
    for item in history:
        observed_at = parse_iso(item.get("observed_at"))
        rain = number(item.get("rain_mm_recent"))
        if observed_at and cutoff <= observed_at <= upper and rain is not None:
            values.append(rain)
    if not values:
        return None
    return max(values)


def pressure_drop(history: list[dict[str, Any]], now: datetime, current: float | None) -> float | None:
    if current is None:
        return None
    cutoff = now - timedelta(hours=12)
    older = []
    for item in history:
        observed_at = parse_iso(item.get("observed_at"))
        pressure = number(item.get("pressure_hpa"))
        if observed_at and cutoff <= observed_at <= now - timedelta(hours=1) and pressure is not None:
            older.append((observed_at, pressure))
    if not older:
        return None
    baseline = max(older, key=lambda row: row[0])[1]
    return baseline - current


def level_for_score(score: int) -> str:
    if score >= 7:
        return "high"
    if score >= 4:
        return "medium"
    return "low"


def zh_level(level: str) -> str:
    return {"high": "高", "medium": "中", "low": "低"}[level]


def build_result(args: argparse.Namespace) -> dict[str, Any]:
    current = fetch_json(CURRENT_WEATHER_URL)
    forecast = fetch_json(FORECAST_URL)
    hourly_rain = fetch_json(HOURLY_RAIN_URL)
    wind_rows = parse_csv_rows(fetch_text(WIND_URL))
    pressure_rows = parse_csv_rows(fetch_text(PRESSURE_URL))

    now = datetime.now(HK_TZ)

    temps = current.get("temperature", {}).get("data", [])
    temp_row = select_by_name(temps, "place", args.temp_place)
    if temp_row is None:
        temp_row = select_by_name(temps, "place", "香港天文台") or (temps[0] if temps else None)
    temp = number(temp_row.get("value") if temp_row else None)

    humidity_rows = current.get("humidity", {}).get("data", [])
    humidity = number(humidity_rows[0].get("value") if humidity_rows else None)

    district_rain = []
    for row in current.get("rainfall", {}).get("data", []):
        rain = number(row.get("max"))
        if rain is not None:
            district_rain.append(rain)
    station_rain = []
    for row in hourly_rain.get("hourlyRainfall", []):
        rain = number(row.get("value"))
        if rain is not None:
            station_rain.append(rain)
    rain_recent = max(district_rain + station_rain) if district_rain or station_rain else None

    wind_row = select_by_name(wind_rows, "Automatic Weather Station", args.wind_station)
    if wind_row is None:
        wind_row = select_by_name(wind_rows, "Automatic Weather Station", "King's Park") or (wind_rows[0] if wind_rows else None)
    wind_speed = number(wind_row.get("10-Minute Mean Speed(km/hour)") if wind_row else None)

    pressure_row = select_by_name(pressure_rows, "Automatic Weather Station", args.pressure_station)
    if pressure_row is None:
        pressure_row = select_by_name(pressure_rows, "Automatic Weather Station", "HK Observatory") or (pressure_rows[0] if pressure_rows else None)
    pressure = number(pressure_row.get("Mean Sea Level Pressure(hPa)") if pressure_row else None)

    observed_at = parse_iso(current.get("updateTime")) or now
    history_path = Path(os.path.expanduser(args.state_file))
    history = load_history(history_path)
    drop = pressure_drop(history, observed_at, pressure)
    stored_rain_24h = max_rain_between(history, observed_at, 24)
    rain_24h_values = [value for value in (rain_recent, stored_rain_24h) if value is not None]
    rain_24h = max(rain_24h_values) if rain_24h_values else None
    rain_24_to_72h = max_rain_between(history, observed_at, 72, 24)

    factors: list[Factor] = []
    unavailable: list[str] = []

    if temp is None:
        unavailable.append("temperature")
    elif temp >= 25:
        factors.append(Factor("temperature", 2, f"{temp:g} C"))
    elif temp >= 20:
        factors.append(Factor("temperature", 1, f"{temp:g} C"))

    if humidity is None:
        unavailable.append("humidity")
    elif humidity >= 80:
        factors.append(Factor("humidity", 2, f"{humidity:g}%"))
    elif humidity >= 70:
        factors.append(Factor("humidity", 1, f"{humidity:g}%"))

    if rain_24h is None:
        unavailable.append("recent_rain")
    elif rain_24h >= 10:
        factors.append(Factor("rain_24h", 2, f"{rain_24h:g} mm"))
    elif rain_24h > 0:
        factors.append(Factor("rain_24h", 1, f"{rain_24h:g} mm"))

    if rain_24_to_72h is not None and rain_24_to_72h > 0:
        factors.append(Factor("rain_24_to_72h", 1, f"{rain_24_to_72h:g} mm stored"))

    if wind_speed is None:
        unavailable.append("wind")
    elif wind_speed < 10:
        factors.append(Factor("weak_wind", 1, f"{wind_speed:g} km/h"))

    if drop is not None and drop >= 2:
        factors.append(Factor("pressure_drop", 1, f"{drop:.1f} hPa drop"))

    if observed_at.hour >= 18 or observed_at.hour < 6:
        factors.append(Factor("evening_or_night", 1, observed_at.strftime("%H:%M")))

    if 4 <= observed_at.month <= 7:
        factors.append(Factor("season", 1, observed_at.strftime("%B")))

    if args.light_on:
        factors.append(Factor("light_on", 1, "strong indoor/outdoor light expected"))

    score = sum(f.points for f in factors)
    level = level_for_score(score)

    history.append(
        {
            "observed_at": observed_at.isoformat(),
            "score": score,
            "level": level,
            "temp_c": temp,
            "humidity_percent": humidity,
            "rain_mm_recent": rain_recent,
            "wind_kmh": wind_speed,
            "pressure_hpa": pressure,
        }
    )
    save_history(history_path, history)

    return {
        "observed_at": observed_at.isoformat(),
        "score": score,
        "level": level,
        "level_zh": zh_level(level),
        "factors": [factor.__dict__ for factor in factors],
        "unavailable": unavailable,
        "readings": {
            "temperature": {"value_c": temp, "place": temp_row.get("place") if temp_row else None},
            "humidity": {"value_percent": humidity, "place": humidity_rows[0].get("place") if humidity_rows else None},
            "rain_recent": {"max_mm": rain_recent, "source": "HKO rhrread + hourlyRainfall"},
            "rain_24h_mm": rain_24h,
            "rain_24_to_72h_stored_mm": rain_24_to_72h,
            "wind": {
                "speed_kmh": wind_speed,
                "station": wind_row.get("Automatic Weather Station") if wind_row else None,
            },
            "pressure": {
                "value_hpa": pressure,
                "station": pressure_row.get("Automatic Weather Station") if pressure_row else None,
                "drop_hpa": None if drop is None or math.isnan(drop) else round(drop, 2),
            },
        },
        "forecast": {
            "generalSituation": forecast.get("generalSituation", ""),
            "forecastDesc": forecast.get("forecastDesc", ""),
            "updateTime": forecast.get("updateTime", ""),
        },
        "data_sources": {
            "current_weather": CURRENT_WEATHER_URL,
            "hourly_rain": HOURLY_RAIN_URL,
            "wind": WIND_URL,
            "pressure": PRESSURE_URL,
            "forecast": FORECAST_URL,
        },
    }


def text_output(result: dict[str, Any]) -> str:
    readings = result["readings"]
    lines = [
        f"飛蟻入屋風險：{result['level_zh']}（{result['score']} 分）",
        f"觀測時間：{result['observed_at']}",
        "",
        "即時讀數：",
        f"- 溫度：{readings['temperature']['value_c']} C（{readings['temperature']['place']}）",
        f"- 濕度：{readings['humidity']['value_percent']}%（{readings['humidity']['place']}）",
        f"- 近雨量：{readings['rain_recent']['max_mm']} mm",
        f"- 風速：{readings['wind']['speed_kmh']} km/h（{readings['wind']['station']}）",
        f"- 氣壓：{readings['pressure']['value_hpa']} hPa（{readings['pressure']['station']}）",
    ]
    if readings["pressure"]["drop_hpa"] is not None:
        lines.append(f"- 氣壓趨勢：下降 {readings['pressure']['drop_hpa']} hPa")
    lines.extend(["", "加分因素："])
    if result["factors"]:
        for factor in result["factors"]:
            lines.append(f"- +{factor['points']} {factor['name']}: {factor['detail']}")
    else:
        lines.append("- 無明顯高危天氣因素")
    if result["unavailable"]:
        lines.extend(["", "未能取得： " + ", ".join(result["unavailable"])])
    forecast = result.get("forecast", {})
    if forecast.get("forecastDesc"):
        lines.extend(["", "天文台預報：", forecast["forecastDesc"]])
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--format", choices=["text", "json"], default="text")
    parser.add_argument("--temp-place", default=None, help="Preferred HKO temperature place, e.g. 沙田")
    parser.add_argument("--wind-station", default=None, help="Preferred wind station in English, e.g. Sha Tin")
    parser.add_argument("--pressure-station", default=None, help="Preferred pressure station in English, e.g. Sha Tin")
    parser.add_argument("--light-on", action="store_true", help="Add risk point for strong lights near windows/balcony")
    parser.add_argument("--state-file", default=str(DEFAULT_STATE), help="History file for rain/pressure trend")
    args = parser.parse_args()

    try:
        result = build_result(args)
    except Exception as exc:  # noqa: BLE001 - CLI should report all retrieval/parsing failures.
        print(f"error: {exc}", file=sys.stderr)
        return 1

    if args.format == "json":
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(text_output(result))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
