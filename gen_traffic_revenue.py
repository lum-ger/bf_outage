import pandas as pd
import numpy as np
import datetime
import time

# --- Configuration: Outage Scenario ---
START_TIME = datetime.datetime(2024, 11, 28, 0, 0, 0)  # Day before Black Friday [cite: 1, 2, 3, 4]
END_TIME = datetime.datetime(2024, 11, 30, 23, 59, 0)  # Day after Black Friday [cite: 1, 2, 3, 4]
INTERVAL_MINUTES = 5  # Data point interval in minutes
OUTAGE_START = datetime.datetime(2024, 11, 29, 10, 0, 0)  # **Outage Start Time (Black Friday)** <-  **MODIFY THIS**
OUTAGE_DURATION_MINUTES = 60  # **Outage Duration in Minutes** <-  **MODIFY THIS**
NORMAL_TRAFFIC_PEAK = 1000  # Normal traffic peak (requests per minute)
BLACK_FRIDAY_PEAK = 5000  # **Black Friday traffic peak multiplier (relative to normal)** <-  **MODIFY THIS**
REVENUE_PER_REQUEST = 0.10  # Average revenue per request
OUTPUT_FILE = "prometheus_traffic_revenue.txt"  # File for Prometheus data

# --- Time Series Creation ---
time_range = pd.date_range(start=START_TIME, end=END_TIME, freq=f'{INTERVAL_MINUTES}min')
df = pd.DataFrame({'timestamp': time_range})


def daily_peak_traffic(time):
    hour = time.hour
    # Simulate a peak around 6 PM
    return int(NORMAL_TRAFFIC_PEAK * np.exp(-((hour - 18) ** 2) / 50))


df['traffic'] = df['timestamp'].apply(daily_peak_traffic)

# Black Friday spike
df['traffic'] = np.where(
    (df['timestamp'].dt.date == datetime.datetime(2024, 11, 29).date()),
    df['traffic'] * (BLACK_FRIDAY_PEAK / NORMAL_TRAFFIC_PEAK),  # Apply Black Friday multiplier
    df['traffic']
)

# Simulate outage
df['traffic'] = np.where(
    (df['timestamp'] >= OUTAGE_START) & (df['timestamp'] < OUTAGE_START + datetime.timedelta(minutes=OUTAGE_DURATION_MINUTES)),
    0,  # Zero traffic during outage
    df['traffic']
)

# Add some noise
df['traffic'] = (df['traffic'] + np.random.normal(0, df['traffic'] * 0.1, len(df))).astype(int)
df['traffic'] = df['traffic'].clip(lower=0).astype(int)  # Ensure no negative traffic

# --- Revenue Calculation ---
df['revenue'] = df['traffic'] * REVENUE_PER_REQUEST
df['revenue'] = df['revenue'].clip(lower=0).astype(int)

# --- Output to Prometheus format ---
with open(OUTPUT_FILE, "w") as f:
    for _, row in df.iterrows():
        timestamp = int(row['timestamp'].timestamp())
        f.write(f"website_traffic {{}} {row['traffic']} {timestamp}\n")
        f.write(f"website_revenue {{}} {row['revenue']} {timestamp}\n")

print(f"Prometheus data written to {OUTPUT_FILE}")