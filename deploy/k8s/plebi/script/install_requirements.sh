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

echo "Installing kube-prometheus..."
git clone https://github.com/prometheus-operator/kube-prometheus.git
cd kube-prometheus

kubectl create -f manifests/setup
kubectl wait \
	--for condition=Established \
	--all CustomResourceDefinition \
	--namespace=monitoring
kubectl apply -f manifests/

kubectl delete networkpolicies --all -n monitoring
kubectl patch service grafana -n monitoring -p '{"spec": {"type": "NodePort"}}'
kubectl patch service prometheus-k8s -n monitoring -p '{"spec": {"type": "NodePort"}}'

echo "kube-prometheus installed successfully."
cd ..

rm -rf kube-prometheus

echo "Installing pushgateway..."
kubectl apply -f pushgateway.yaml
echo "pushgateway installed successfully."

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