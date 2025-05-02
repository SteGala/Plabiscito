import os
import pandas as pd
import matplotlib.pyplot as plt
import re
import seaborn as sns
import numpy as np


def parse_bandwidth(value):
    if pd.isna(value):
        return None
    value = str(value)
    match = re.match(r"([\d.]+)\s*(Gb/s|Mb/s)", value)
    if not match:
        return None
    number, unit = match.groups()
    number = float(number)
    if unit == "Mb/s":
        return number / 1000  # Convert to Gb/s
    return number  # Already in Gb/s

def plot_failure_severity(base_path, file_id=0, filename=None):  
    data = {}

    for dir_name in sorted(os.listdir(base_path)):
        occ = {}
        dir_path = os.path.join(base_path, dir_name)
        if os.path.isdir(dir_path):
            files = [f for f in os.listdir(dir_path) if f.endswith('.csv')]
            if not files:
                continue

            csv_path = os.path.join(dir_path, sorted(files)[file_id])
            df = pd.read_csv(csv_path)

            # iterate over the column names
            for col in df.columns:
                if col == "Time":
                    continue
                
                # split the column name based on the character @
                parts = col.split("@")

                if parts[1] not in occ:
                    occ[parts[1]] = 0
                
                if "server" in parts[0]:
                    occ[parts[1]] += 1

            data[dir_name] = []
            for key in occ:
                data[dir_name].append(occ[key])

    # Convert to a long-format DataFrame
    rows = []
    for label, values in data.items():
        for v in values:
            rows.append({"Algorithm": label, "Failed applications": v})
    df = pd.DataFrame(rows)

    # Plot
    sns.barplot(data=df, x="Algorithm", y="Failed applications", estimator="mean", errorbar=None, color="red", alpha=0.5)
    sns.stripplot(data=df, x="Algorithm", y="Failed applications", color="black", size=6, jitter=False)
    plt.tight_layout()
    plt.savefig(filename)  
    plt.clf()  # Clear the figure for the next plot

def plot_bandwidth_boxplots(base_path, file_id=0, filename=None):
    all_data = []

    for dir_name in sorted(os.listdir(base_path)):
        dir_path = os.path.join(base_path, dir_name)
        if os.path.isdir(dir_path):
            files = [f for f in os.listdir(dir_path) if f.endswith('.csv')]
            if not files:
                continue

            csv_path = os.path.join(dir_path, sorted(files)[file_id])
            df = pd.read_csv(csv_path)

            numeric_df = df.drop(columns=['Time']).map(parse_bandwidth)
            for value in numeric_df.values.flatten():
                all_data.append({'Bandwidth': value, 'Algorithm': dir_name})

    # Convert to DataFrame for Seaborn
    plot_df = pd.DataFrame(all_data)

    #plt.figure(figsize=(12, 6))
    sns.violinplot(x='Algorithm', y='Bandwidth', data=plot_df, inner='box', cut=0)
    plt.ylabel("Network Traffic (Gb/s)")
    plt.grid(True, linestyle="--", alpha=0.5)
    plt.tight_layout()
    plt.savefig(filename)
    plt.clf()  # Clear the figure for the next plot

def plot_cdfs_from_directories(base_path, file_id=0, file_name=None):
    plt.figure(figsize=(10, 6))

    for dir_name in sorted(os.listdir(base_path)):
        dir_path = os.path.join(base_path, dir_name)
        if os.path.isdir(dir_path):
            files = [f for f in os.listdir(dir_path) if f.endswith('.csv')]
            if not files:
                continue

            csv_path = os.path.join(dir_path, sorted(files)[file_id])
            df = pd.read_csv(csv_path)

            # Drop Time and flatten values
            values = df.drop(columns=['Time']).values.flatten()
            values = pd.to_numeric(values, errors='coerce')
            values = values[~pd.isnull(values)]  # Drop NaNs

            # Sort and compute CDF
            sorted_vals = np.sort(values)
            cdf = np.arange(1, len(sorted_vals) + 1) / len(sorted_vals)

            # Plot CDF
            plt.plot(sorted_vals, cdf, label=dir_name)

    plt.xlabel("Training Time (s)")
    plt.ylabel("CDF")
    plt.legend(title="Algorithms", bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.grid(True, linestyle="--", alpha=0.6)
    plt.tight_layout()
    plt.savefig(file_name)
    plt.clf()  # Clear the figure for the next plot

plot_failure_severity(".", 0, "failure_severity.pdf")
plot_bandwidth_boxplots(".", 1, "rx_bandwidth_interface.pdf")
plot_bandwidth_boxplots(".", 2, "rx_bandwidth_localhost.pdf")
plot_bandwidth_boxplots(".", 3, "tx_bandwidth_interface.pdf")
plot_bandwidth_boxplots(".", 4, "tx_bandwidth_localhost.pdf")
plot_cdfs_from_directories(".", 5, "training_time.pdf")