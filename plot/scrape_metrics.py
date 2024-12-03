import requests
import time
import csv
import argparse
from datetime import datetime

def fetch_prometheus_metric(prometheus_url, query):
    """Fetch the specified query from the Prometheus server."""
    try:
        response = requests.get(f"{prometheus_url}/api/v1/query", params={"query": query})
        response.raise_for_status()
        data = response.json()

        if data["status"] == "success":
            return data["data"]["result"]
        else:
            print(f"Error fetching metric: {data.get('error', 'Unknown error')}")
            return []
    except requests.RequestException as e:
        print(f"Error connecting to Prometheus: {e}")
        return []

def save_to_csv(file_name, metric_data):
    """Save the scraped metric data into a CSV file."""
    try:
        with open(file_name, mode="a", newline="") as csv_file:
            writer = csv.writer(csv_file)
            metric_value = []
            timestamp = None

            # Write the rows for each node (instance)
            for instance in metric_data:
                value = instance.get("value", [])
                timestamp = datetime.fromtimestamp(float(value[0]))
                metric_value.append(value[1])

            if timestamp is None:
                writer.writerow([0, [0]])
                return
            # Write data to CSV
            writer.writerow([timestamp, metric_value])

    except IOError as e:
        print(f"Error writing to CSV file: {e}")

def main():
    parser = argparse.ArgumentParser(description="Scrape Prometheus metrics and save to CSV.")
    parser.add_argument("ip", type=str, help="Prometheus server IP address.")
    parser.add_argument("port", type=int, help="Prometheus server port.")

    args = parser.parse_args()

    prometheus_url = f"http://{args.ip}:{args.port}"

    # Query string for the CPU utilization metric
    query_cpu = f"""
    instance:node_cpu_utilisation:rate5m * instance:node_num_cpu:sum
    """

    query_transmit = f"""
    instance:node_network_transmit_bytes_excluding_lo:rate5m != 0
    """

    query_receive = f"""
    instance:node_network_receive_bytes_excluding_lo:rate5m != 0
    """

    query_training_time = f"""
    training_time
    """

    # Write CSV header
    with open("cpu_usage.csv", mode="w", newline="") as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(["timestamp", "value"])

    with open("bw_transmit.csv", mode="w", newline="") as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(["timestamp", "value"])

    with open("bw_receive.csv", mode="w", newline="") as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(["timestamp", "value"])

    with open("training_time.csv", mode="w", newline="") as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(["timestamp", "value"])

    while True:
        metric_data = fetch_prometheus_metric(prometheus_url, query_cpu)
        save_to_csv("cpu_usage.csv", metric_data)

        metric_data = fetch_prometheus_metric(prometheus_url, query_transmit)
        save_to_csv("bw_transmit.csv", metric_data)

        metric_data = fetch_prometheus_metric(prometheus_url, query_receive)
        save_to_csv("bw_receive.csv", metric_data)

        metric_data = fetch_prometheus_metric(prometheus_url, query_training_time)
        save_to_csv("training_time.csv", metric_data)

        time.sleep(15)

if __name__ == "__main__":
    main()
