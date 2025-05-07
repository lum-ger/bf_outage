import pandas as pd
import numpy as np
import datetime
import time

# --- Configuration: Outage Scenario ---
START_TIME = datetime.datetime(2024, 11, 28, 0, 0, 0)
END_TIME = datetime.datetime(2024, 11, 30, 23, 59, 0)
INTERVAL_MINUTES = 5
SLOWDOWN_START = datetime.datetime(2024, 11, 29, 14, 0, 0)  # **Slowdown Start Time (Black Friday)** <-  **MODIFY THIS**
SLOWDOWN_DURATION_MINUTES = 120  # **Slowdown Duration in Minutes** <-  **MODIFY THIS**
ENDPOINTS = ['/product', '/cart', '/checkout', '/search']
BASE_RESPONSE_TIME = 200
OUTPUT_FILE = "prometheus_app_performance.txt"

# --- Time Series Creation ---
time_range = pd.date_range(start=START_TIME, end=END_TIME, freq=f'{INTERVAL_MINUTES}min')
df_app = pd.DataFrame({'timestamp': time_range})

# --- Simulate Response Times ---
for endpoint in ENDPOINTS:
    df_app[endpoint] = BASE_RESPONSE_TIME + np.random.normal(0, BASE_RESPONSE_TIME * 0.1, len(df_app))

    # Simulate slowdown
    df_app[endpoint] = np.where(
        (df_app['timestamp'] >= SLOWDOWN_START) & (df_app['timestamp'] < SLOWDOWN_START + datetime.timedelta(minutes=SLOWDOWN_DURATION_MINUTES)),
        df_app[endpoint] * 3,  # Increase response time
        df_app[endpoint]
    )
    df_app[endpoint] = df_app[endpoint].clip(lower=0).astype(int)
    df_app[endpoint] = df_app[endpoint].astype(int)

# --- Output to Prometheus format ---
with open(OUTPUT_FILE, "w") as f:
    for _, row in df_app.iterrows():
        timestamp = int(row['timestamp'].timestamp())
        for endpoint in ENDPOINTS:
            f.write(f"app_response_time{{endpoint=\"{endpoint}\"}} {row[endpoint]} {timestamp}\n")

print(f"Prometheus data written to {OUTPUT_FILE}")