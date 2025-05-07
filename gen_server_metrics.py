import pandas as pd
import numpy as np
import datetime
import time

# --- Configuration: Scaling/Outage Scenario ---
START_TIME = datetime.datetime(2024, 11, 28, 0, 0, 0)
END_TIME = datetime.datetime(2024, 11, 30, 23, 59, 0)
INTERVAL_MINUTES = 5
SCALING_ISSUE_START = datetime.datetime(2024, 11, 30, 12, 0, 0)  # **Scaling Issue Start Time** <-  **MODIFY THIS**
SCALING_ISSUE_DURATION_MINUTES = 180  # **Scaling Issue Duration in Minutes** <-  **MODIFY THIS**
BASE_CPU_UTIL = 20  # Percentage
BASE_MEMORY_UTIL = 50
BLACK_FRIDAY_IMPACT_ON_SERVER = 30  # **CPU increase during Black Friday** <- **MODIFY THIS**
SCALING_IMPACT_ON_SERVER = 30  # **CPU increase during Scaling issue** <- **MODIFY THIS**
OUTPUT_FILE = "prometheus_server_metrics.txt"

# --- Time Series Creation ---
time_range = pd.date_range(start=START_TIME, end=END_TIME, freq=f'{INTERVAL_MINUTES}min')
df_server = pd.DataFrame({'timestamp': time_range})

# --- Simulate CPU Utilization ---
df_server['cpu_util'] = BASE_CPU_UTIL + np.random.normal(0, 5, len(df_server))

# Increase CPU during Black Friday and scaling issue
df_server['cpu_util'] = np.where(
    (df_server['timestamp'].dt.date == datetime.datetime(2024, 11, 29).date()) |  # Corrected line!
    ((df_server['timestamp'] >= SCALING_ISSUE_START) & (df_server['timestamp'] < SCALING_ISSUE_START + datetime.timedelta(minutes=SCALING_ISSUE_DURATION_MINUTES))),
    df_server['cpu_util'] + BLACK_FRIDAY_IMPACT_ON_SERVER,  # Using the variable
    df_server['cpu_util']
)
df_server['cpu_util'] = df_server['cpu_util'].clip(lower=0, upper=100).astype(int)

# --- Simulate Memory Utilization ---
df_server['memory_util'] = BASE_MEMORY_UTIL + np.random.normal(0, 5, len(df_server))
df_server['memory_util'] = df_server['memory_util'].clip(lower=0, upper=100).astype(int)

# --- Output to Prometheus format ---
with open(OUTPUT_FILE, "w") as f:
    for _, row in df_server.iterrows():
        timestamp = int(row['timestamp'].timestamp())
        f.write(f"server_cpu_util {{}} {row['cpu_util']} {timestamp}\n")
        f.write(f"server_memory_util {{}} {row['memory_util']} {timestamp}\n")

print(f"Prometheus data written to {OUTPUT_FILE}")