---
name: flying-ant-risk-hk
description: Check real-time Hong Kong Observatory weather data and estimate the chance of a large flying termite/winged ant swarm entering homes in Hong Kong, using temperature, humidity, rainfall, wind, pressure, season, and evening light-risk heuristics.
---

# Flying Ant Risk HK

Use this skill when the user asks whether tonight is a high-risk "大水蟻/飛蟻入屋" period in Hong Kong, wants a current risk score, or wants an agent-native weather heuristic for flying termite swarms.

Run the bundled CLI for deterministic scoring:

```bash
python3 skills/flying-ant-risk-hk/scripts/flying_ant_risk.py
```

Useful options:

```bash
python3 skills/flying-ant-risk-hk/scripts/flying_ant_risk.py --format text
python3 skills/flying-ant-risk-hk/scripts/flying_ant_risk.py --format json
python3 skills/flying-ant-risk-hk/scripts/flying_ant_risk.py --light-on
python3 skills/flying-ant-risk-hk/scripts/flying_ant_risk.py --temp-place "沙田" --wind-station "Sha Tin" --pressure-station "Sha Tin"
```

## Workflow

1. Run the CLI with `--format text` unless structured JSON is needed.
2. If the user gives their district, pass the nearest HKO temperature place and wind/pressure station.
3. Treat pressure trend as optional. The script stores previous observations in `~/.openclaw/state/flying-ant-risk-hk/history.json` and only awards pressure-trend points when enough history exists.
4. Reply in Traditional Chinese by default. Include score, level, and the strongest trigger factors.

## Risk Model

The score follows this practical Hong Kong home heuristic:

- Temperature >= 25 C: +2
- Relative humidity >= 80%: +2
- Rain observed within 24 hours, including current HKO rainfall feeds: +1, or >= 10 mm: +2
- Rain observed 24-72 hours ago from stored history: +1
- Wind speed < 10 km/h: +1
- Pressure has dropped by >= 2 hPa within stored history: +1
- Current local time is evening/night: +1
- Month is April to July: +1
- `--light-on`: +1

Levels:

- 0-3: low
- 4-6: medium
- 7+: high

## Data Sources

See `references/data_sources.md` for the HKO endpoints and notes.

## Caveats

This is a risk heuristic, not a biological certainty. It cannot know whether there is a mature nearby termite colony, indoor light leakage, window gaps, or the exact species. If source data is missing, the script reports unavailable factors rather than inventing values.
