echo "Additional informations:"

# Get the service in the plebi namespace of type nodeport
SERVICE=$(kubectl get service grafana -n monitoring -o jsonpath='{.spec.ports[0].nodePort}')

# Get the IP address of the nodes
NODE_IPS=$(kubectl get nodes -o jsonpath='{.items[*].status.addresses[?(@.type=="InternalIP")].address}')
echo "The Grafana dashboard is available at http://[$NODE_IPS]:$SERVICE"

# Get the service in the plebi namespace of type nodeport
SERVICE=$(kubectl get service prometheus-k8s -n monitoring -o jsonpath='{.spec.ports[0].nodePort}')

echo "The Prometheus dashboard is available at http://[$NODE_IPS]:$SERVICE"

echo "Check the status of Plebiscito deployment using 'kubectl get pods -n plebi'."

# Get the service in the plebi namespace of type nodeport
SERVICE=$(kubectl get svc -n plebi -o jsonpath='{.items[0].spec.ports[0].nodePort}')

# Get the IP address of the nodes
echo "Plebiscito service is available at http://[$NODE_IPS]:$SERVICE"
echo "Use these values to communicate with Plebiscito using the provided client under /src/plebiscito_client.py"
echo "Flower instances will be deployed under the offloaded-namespace in kubernetes. You can check the status by typing 'kubectl get pods -n offloaded-namespace -o wide'." 