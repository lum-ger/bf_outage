import pandas as pd
import numpy as np
import datetime
import time
import json

# --- Configuration: Outage Scenario ---
START_TIME = datetime.datetime(2024, 11, 28, 0, 0, 0)
END_TIME = datetime.datetime(2024, 11, 30, 23, 59, 0)
INTERVAL_MINUTES = 5
OUTAGE_START = datetime.datetime(2024, 11, 29, 10, 0, 0)
OUTAGE_DURATION_MINUTES = 60
NORMAL_TRAFFIC_PEAK = 1000
BLACK_FRIDAY_PEAK = 5000
REVENUE_PER_REQUEST = 0.10
OUTPUT_FILE = "traffic_revenue_grafana.json"  # Changed output file name

# --- Time Series Creation ---
time_range = pd.date_range(start=START_TIME, end=END_TIME, freq=f'{INTERVAL_MINUTES}min')
df = pd.DataFrame({'timestamp': time_range})


def daily_peak_traffic(time):
    hour = time.hour
    return int(NORMAL_TRAFFIC_PEAK * np.exp(-((hour - 18) ** 2) / 50))


df['traffic'] = df['timestamp'].apply(daily_peak_traffic)
df['traffic'] = np.where(
    (df['timestamp'].dt.date == datetime.datetime(2024, 11, 29).date()),
    df['traffic'] * (BLACK_FRIDAY_PEAK / NORMAL_TRAFFIC_PEAK),
    df['traffic']
)
df['traffic'] = np.where(
    (df['timestamp'] >= OUTAGE_START) & (df['timestamp'] < OUTAGE_START + datetime.timedelta(minutes=OUTAGE_DURATION_MINUTES)),
    0,
    df['traffic']
)
df['traffic'] = (df['traffic'] + np.random.normal(0, df['traffic'] * 0.1, len(df))).astype(int)
df['traffic'] = df['traffic'].clip(lower=0).astype(int)
df['revenue'] = df['traffic'] * REVENUE_PER_REQUEST
df['revenue'] = df['revenue'].clip(lower=0).astype(int)

# --- Output to Grafana format (JSON) ---
data_points = []
for _, row in df.iterrows():
    timestamp = int(row['timestamp'].timestamp())
    data_points.append({
        'time': timestamp,
        'traffic': int(row['traffic']),
        'revenue': row['revenue']
    })

with open(OUTPUT_FILE, "w") as f:
    json.dump(data_points, f, indent=2)

print(f"Grafana-friendly data written to {OUTPUT_FILE}")