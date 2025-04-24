#!/bin/bash

function check_kubectl() {
    if ! command -v kubectl &> /dev/null; then
        echo "Error: kubectl is not installed. Please install it to use this script."
        exit 1
    fi
}

check_kubectl

echo "Fetching the list of nodes in the Kubernetes cluster..."
nodes=$(kubectl get nodes -o name)

if [ -z "$nodes" ]; then
    echo "No nodes found in the cluster. Exiting."
    exit 0
fi

echo "Installing Prometheus..."

export KUBECONFIG=/etc/rancher/k3s/k3s.yaml
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update
helm install prometheus prometheus-community/kube-prometheus-stack --namespace monitoring --create-namespace --set grafana.service.type=NodePort --set prometheus.service.type=NodePort --set prometheus-node-exporter.prometheus.monitor.interval=10s
helm install pushgateway prometheus-community/prometheus-pushgateway --set serviceMonitor.enabled=true --set serviceMonitor.additionalLabels.release=prometheus --namespace monitoring

echo "Setup completed successfully."

sleep 2

# Get the service in the plebi namespace of type nodeport
SERVICE=$(kubectl get service grafana -n monitoring -o jsonpath='{.spec.ports[0].nodePort}')

# Get the IP address of the nodes
NODE_IPS=$(kubectl get nodes -o jsonpath='{.items[*].status.addresses[?(@.type=="InternalIP")].address}')
echo "The Grafana dashboard is available at http://[$NODE_IPS]:$SERVICE"

# Get the service in the plebi namespace of type nodeport
SERVICE=$(kubectl get service prometheus-k8s -n monitoring -o jsonpath='{.spec.ports[0].nodePort}')

echo "The Prometheus dashboard is available at http://[$NODE_IPS]:$SERVICE"