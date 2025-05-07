import pandas as pd
import numpy as np
import datetime
import time
import json

# --- Configuration: Scaling/Outage Scenario ---
START_TIME = datetime.datetime(2024, 11, 28, 0, 0, 0)
END_TIME = datetime.datetime(2024, 11, 30, 23, 59, 0)
INTERVAL_MINUTES = 5
SCALING_ISSUE_START = datetime.datetime(2024, 11, 30, 12, 0, 0)
SCALING_ISSUE_DURATION_MINUTES = 180
BASE_CPU_UTIL = 20
BASE_MEMORY_UTIL = 50
BLACK_FRIDAY_IMPACT_ON_SERVER = 30
SCALING_IMPACT_ON_SERVER = 30
OUTPUT_FILE = "server_metrics_targets.json"  # Changed output file name

# --- Time Series Creation ---
time_range = pd.date_range(start=START_TIME, end=END_TIME, freq=f'{INTERVAL_MINUTES}min')
df_server = pd.DataFrame({'timestamp': time_range})

# --- Simulate CPU Utilization ---
df_server['cpu_util'] = BASE_CPU_UTIL + np.random.normal(0, 5, len(df_server))
df_server['cpu_util'] = np.where(
    (df_server['timestamp'].dt.date == datetime.datetime(2024, 11, 29).date()) |
    ((df_server['timestamp'] >= SCALING_ISSUE_START) & (df_server['timestamp'] < SCALING_ISSUE_START + datetime.timedelta(minutes=SCALING_ISSUE_DURATION_MINUTES))),
    df_server['cpu_util'] + BLACK_FRIDAY_IMPACT_ON_SERVER,
    df_server['cpu_util']
)
df_server['cpu_util'] = df_server['cpu_util'].clip(lower=0, upper=100).astype(int)

# --- Simulate Memory Utilization ---
df_server['memory_util'] = BASE_MEMORY_UTIL + np.random.normal(0, 5, len(df_server))
df_server['memory_util'] = df_server['memory_util'].clip(lower=0, upper=100).astype(int)

# --- Output to Prometheus format (JSON for file_sd) ---
targets = [{
    'targets': ['dummy_host'],
    'labels': {}
}]
metrics = []
for _, row in df_server.iterrows():
    timestamp = int(row['timestamp'].timestamp())
    metrics.append(f"server_cpu_util {{timestamp=\"{timestamp}\"}} {row['cpu_util']}")
    metrics.append(f"server_memory_util {{timestamp=\"{timestamp}\"}} {row['memory_util']}")
targets[0]['labels']['__meta_static_metrics'] = '\n'.join(metrics)

with open(OUTPUT_FILE, "w") as f:
    json.dump([targets[0]], f, indent=2)

print(f"Prometheus data written to {OUTPUT_FILE}")