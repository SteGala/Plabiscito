import os
import sys

from src.network import Endpoint
from src.plebiscito_node import PNode
from src.config import Environment

def read_env_variable():
    # get node ID
    node_id = os.getenv('ID', -1)
    
    if node_id == -1:
        print("Error: ID not found")
        sys.exit(1)
    
    try:
        node_id = int(node_id)
    except ValueError:
        print("Error: Node ID must an integer")
        sys.exit(1)

    address = os.getenv('ADDRESS', "localhost")
    port = os.getenv('PORT', 5551)

    neighbors = os.getenv('NEIGHBORS', "")
    if neighbors == "":
        print("[WARNING]: No neighbors specified.")
    else:
        neighbors = neighbors.split(",")
        neighbors = [x.split(":") for x in neighbors]
        neighbors = [(x[0], x[1]) for x in neighbors]

    return node_id, address, port, neighbors

if __name__ == '__main__':
    print("Starting Plebiscito")
    print("Reading environment variables")

    nodeId, address, port, neighbors = read_env_variable()

    print(f"Starting Plebiscito node instance {nodeId} at {address}:{port}")

    neighbors_ep = []
    for neighbor in neighbors:
        neighbors_ep.append(Endpoint("e", neighbor[0], neighbor[1]))

    self_ep = Endpoint("e", address, port)
    node = PNode(id=nodeId, self_ep=self_ep, neighbors_ep=neighbors_ep, env=Environment.KUBERNETES)
    node.start_daemon()