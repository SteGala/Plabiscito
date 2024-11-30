#!/bin/bash

# Path to the template file
TEMPLATE_FILE="deployment_template.yaml"
# Temporary file to hold the customized manifest
TEMP_FILE="custom_deployment.yaml"

# Function to check if kubectl is installed
function check_kubectl() {
    if ! command -v kubectl &> /dev/null; then
        echo "Error: kubectl is not installed. Please install it to use this script."
        exit 1
    fi
}

# Function to check if required arguments are provided
function check_arguments() {
    if [ -z "$CPU" ] || [ -z "$GPU" ] || [ -z "$MEMORY" ] || [ -z "$BW" ] || [ -z "$UTILITY" ]; then
        echo "Usage: $0 <cpu> <gpu> <memory> <bw> <utility> <bw_issue_nodes>"
        echo "  <cpu>            Available CPU resources for each node."
        echo "  <gpu>            Available GPU resources for each node."
        echo "  <memory>         Available memory resources for each node."
        echo "  <bw>             Default bandwidth for nodes."
        echo "  <utility>        Utility function to use for customization (LGF/SGF supported)."
        echo "  <bw_issue_nodes> Comma-separated list of nodes with bandwidth issues."
        exit 1
    fi
}

# Read arguments
CPU=$1
GPU=$2
MEMORY=$3
BW=$4
UTILITY=$5
BW_ISSUE_NODES=$6

# Validate arguments
check_arguments

# Convert the list of nodes with bandwidth issues into an array
IFS=',' read -r -a BW_ISSUE_NODES_ARRAY <<< "$BW_ISSUE_NODES"

# Check kubectl availability
check_kubectl

# Verify template file exists
if [ ! -f "$TEMPLATE_FILE" ]; then
    echo "Error: Template file '$TEMPLATE_FILE' not found."
    exit 1
fi

# Get the list of nodes in the cluster
echo "Fetching the list of nodes in the Kubernetes cluster..."
nodes=$(kubectl get nodes -o name)

if [ -z "$nodes" ]; then
    echo "No nodes found in the cluster. Exiting."
    exit 0
fi

# Count the number of nodes
node_count=$(echo "$nodes" | wc -l)
echo "Detected $node_count node(s) in the cluster."

echo "Creating the namespace 'plebi'..."
kubectl create namespace plebi

echo "Creating the namespace 'offloaded-namespace'..."
kubectl create namespace offloaded-namespace

echo "Applying permissions for the namespace 'plebi'..."
kubectl apply -f permissions.yml

# Loop through each node and perform actions
echo "Starting customization and application for each node..."
count=0
for node in $nodes; do
    # Extract node name from 'node/' prefix
    node_name=${node#node/}
    echo "Processing node: $node_name"

    ENDPOINTS=""
    count2=0
    for node2 in $nodes; do
        node2_name=${node2#node/}
        if [ "$node_name" != "$node2_name" ]; then
            if [ "$ENDPOINTS" != "" ]; then
                ENDPOINTS="$ENDPOINTS,"
            fi
            ENDPOINTS="${ENDPOINTS}$node2_name:$count2:plebi-$node2_name.plebi.svc.cluster.local:5000"
        fi
        count2=$((count2+1))
    done 

    # Check if the node is in the bandwidth issue list
    if [[ " ${BW_ISSUE_NODES_ARRAY[@]} " =~ " ${node_name} " ]]; then
        NODE_BW=1
        echo "Node $node_name has limited bandwidth. Using 1 as the bandwidth value."
    else
        NODE_BW="$BW"
        echo "Node $node_name has default bandwidth: $NODE_BW."
    fi

    SERVICE_TYPE="ClusterIP"
    if [ $count -eq 0 ]; then
        SERVICE_TYPE="NodePort"
    fi

    # Customize the template
    echo "Customizing the template for node: $node_name..."
    sed -e "s/{{ID}}/$count/g" \
        -e "s/{{NODE_NAME}}/$node_name/g" \
        -e "s/{{CPU}}/$CPU/g" \
        -e "s/{{GPU}}/$GPU/g" \
        -e "s/{{MEMORY}}/$MEMORY/g" \
        -e "s/{{BW}}/$NODE_BW/g" \
        -e "s/{{UTILITY}}/$UTILITY/g" \
        -e "s/{{NEIGHBORS_LIST}}/$ENDPOINTS/g" \
        -e "s/{{SERVICE_TYPE}}/$SERVICE_TYPE/g" \
        "$TEMPLATE_FILE" > "$TEMP_FILE"

    # Apply the customized template
    echo "Applying the customized template to the cluster for node: $node_name..."
    kubectl apply -f "$TEMP_FILE"

    # Check the result
    if [ $? -eq 0 ]; then
        echo "Template successfully applied for node: $node_name"
    else
        echo "Failed to apply template for node: $node_name"
    fi

    echo "Finished processing node: $node_name"
    echo "-----------------------------"
    count=$((count+1))
done

rm $TEMP_FILE
echo "All actions completed for all nodes."
echo "-----------------------------"
echo "Additional informations:"
echo "Check the status of Plebiscito deployment using 'kubectl get pods -n plebi'."

# Get the service in the plebi namespace of type nodeport
SERVICE=$(kubectl get svc -n plebi -o jsonpath='{.items[0].spec.ports[0].nodePort}')

# Get the IP address of the nodes
NODE_IPS=$(kubectl get nodes -o jsonpath='{.items[*].status.addresses[?(@.type=="InternalIP")].address}')
echo "Plebiscito service is available at http://[$NODE_IPS]:$SERVICE"
echo "Use these values to communicate with Plebiscito using the provided client under /src/plebiscito_client.py"
echo "Flower instances will be deployed under the offloaded-namespace in kubernetes. You can check the status by typing 'kubectl get pods -n offloaded-namespace -o wide'." 