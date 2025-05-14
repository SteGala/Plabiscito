import os
import pandas as pd
import matplotlib as mat
import re
import seaborn as sns
import numpy as np
import tikzplotlib


tot_nodes = 6

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

            if len(occ) < tot_nodes:
                for i in range(tot_nodes - len(occ)):
                    data[dir_name].append(0)

    # Convert to a long-format DataFrame
    rows = []
    for label, values in data.items():
        for v in values:
            rows.append({"Algorithm": label, "Failed applications": v})
    df = pd.DataFrame(rows)

    # Plot
    sns.barplot(data=df, x="Algorithm", y="Failed applications", estimator="mean", errorbar=None, color="red", alpha=0.5)
    sns.stripplot(data=df, x="Algorithm", y="Failed applications", color="black", size=6, jitter=True)
    mat.pyplot.tight_layout()
    mat.pyplot.savefig(filename)  
    tikzplotlib.save(filename)

    mat.pyplot.clf()  # Clear the figure for the next plot

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

    #mat.pyplot.figure(figsize=(12, 6))
    sns.violinplot(x='Algorithm', y='Bandwidth', data=plot_df, inner='box', cut=0)
    mat.pyplot.ylabel("Network Traffic (Gb/s)")
    mat.pyplot.grid(True, linestyle="--", alpha=0.5)
    mat.pyplot.tight_layout()
    mat.pyplot.savefig(filename)
    mat.pyplot.clf()  # Clear the figure for the next plot

def plot_cdfs_from_directories(base_path, file_id=0, file_name=None):
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
            mat.pyplot.plot(sorted_vals, cdf, label=dir_name)

    mat.pyplot.xlabel("Training Time (s)")
    mat.pyplot.ylabel("CDF")
    mat.pyplot.legend(title="Algorithms")
    mat.pyplot.grid(True, linestyle="--", alpha=0.6)
    mat.pyplot.tight_layout()
    mat.pyplot.savefig(file_name)
    mat.pyplot.clf()  # Clear the figure for the next plot

mat.pyplot.figure(figsize=(6, 3))
font = {"size": 14}

mat.rc('font', **font)

plot_failure_severity(".", 0, "failure_severity.pdf")
plot_bandwidth_boxplots(".", 1, "rx_bandwidth_interface.pdf")
plot_bandwidth_boxplots(".", 2, "rx_bandwidth_localhost.pdf")
plot_bandwidth_boxplots(".", 3, "tx_bandwidth_interface.pdf")
plot_bandwidth_boxplots(".", 4, "tx_bandwidth_localhost.pdf")
plot_cdfs_from_directories(".", 5, "training_time.pdf")