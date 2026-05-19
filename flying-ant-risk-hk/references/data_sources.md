# HKO Data Sources

Primary endpoints used by `scripts/flying_ant_risk.py`:

- Current weather report JSON:
  `https://data.weather.gov.hk/weatherAPI/opendata/weather.php?dataType=rhrread&lang=tc`
- Latest 10-minute wind CSV:
  `https://data.weather.gov.hk/weatherAPI/hko_data/regional-weather/latest_10min_wind.csv`
- Rainfall in the past hour JSON:
  `https://data.weather.gov.hk/weatherAPI/opendata/hourlyRainfall.php?lang=tc`
- Latest 1-minute mean sea level pressure CSV:
  `https://data.weather.gov.hk/weatherAPI/hko_data/regional-weather/latest_1min_pressure.csv`
- Local weather forecast JSON, used for human-readable context only:
  `https://data.weather.gov.hk/weatherAPI/opendata/weather.php?dataType=flw&lang=tc`

User-provided DATA.GOV.HK resource pages:

- Current weather report:
  `https://data.gov.hk/tc-data/dataset/hk-hko-rss-current-weather-report/resource/b1dcb267-b1af-409d-af9b-6b8301aec77a`
- Latest ten-minute wind:
  `https://data.gov.hk/tc-data/dataset/hk-hko-rss-latest-ten-minute-wind-info/resource/06c4729d-cc2e-4ae0-b428-32351ced35f6`
- Rainfall in the past hour:
  `https://data.gov.hk/tc-data/dataset/hk-hko-rss-rainfall-in-the-past-hour/resource/eda01821-ef71-4ed3-9edb-38ad7ae5ac6e`
- HKO Open Data overview:
  `https://www.hko.gov.hk/tc/abouthko/opendata_intro.htm`

Notes:

- `rhrread` has current temperature, humidity, and district rainfall.
- The wind and pressure feeds are CSV and use English station names.
- HKO pressure feed is latest-only. Pressure trend is derived from locally stored previous readings after this skill has run for a while.
- The hourly rainfall endpoint gives a station list, while `rhrread.rainfall` gives district rainfall. The script uses the maximum available recent rainfall as a conservative local trigger.
