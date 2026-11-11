# SHECodes — Mauritius Traffic Mobility Prototype

## What this app does
- Uses the Mauritius Open Data Portal CSV `length-and-density-of-road-network.csv` (1980–2024).
- Shows real historical road-network indicators and road-category trends.
- Calculates total road length from the published categories.
- Provides an interactive before/after journey scenario calculator.
- Exports the user's scenario comparison to CSV.

## Important data limitation
The official road dataset is island-wide annual statistics. It does not contain road geometry, live traffic speeds, corridor-level congestion, bus arrival times, or observed Port Louis–Curepipe journey times. The scenario planner is therefore a transparent what-if calculator, not an AI forecast. Replace its example values with measured observations or verified timetable values before claiming real-world savings.

## Run locally
1. Install Python 3.10 or newer.
2. Open a terminal in this folder.
3. Run: `python -m pip install -r requirements.txt`
4. Run: `streamlit run app.py`
5. Open the local URL shown in the terminal.

## Data source and licence
Mauritius Open Data Portal — “Length and density of road network for the Island of Mauritius”
https://data.govmu.org/dataset/length-density-road-network-island-mauritius
Licence: CC-BY-SA-4.0
