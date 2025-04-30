import os
import sys

from src.network import Endpoint
from src.plebiscito_node import PNode
from src.config import Environment, str_to_utility

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

    node_name = os.getenv('NAME', -1)
    
    if node_name == -1:
        print("Error: Node name not found")
        sys.exit(1)

    address = os.getenv('ADDRESS', "localhost")
    port = os.getenv('PORT', 5551)

    neighbors = os.getenv('NEIGHBORS', "")
    if neighbors == "":
        print("[WARNING]: No neighbors specified.")
    else:
        neighbors = neighbors.split(",")
        neighbors = [x.split(":") for x in neighbors]
        neighbors = [(x[0], x[1], x[2], x[3], x[4]) for x in neighbors]

    cpu = os.getenv('CPU', -1)
    if cpu == -1:
        print("Error: CPU available not found")
        sys.exit(1)
    try:
        cpu = float(cpu)
    except ValueError:
        print("Error: Node CPU must an float")
        sys.exit(1)
        cpu = os.getenv('CPU', -1)
    
    gpu = os.getenv('GPU', -1)
    if gpu == -1:
        print("Error: CPU available not found")
        sys.exit(1)
    try:
        gpu = float(gpu)
    except ValueError:
        print("Error: Node GPU must an float")
        sys.exit(1)

    mem = os.getenv('MEM', -1)
    if cpu == -1:
        print("Error: MEM available not found")
        sys.exit(1)
    try:
        mem = float(mem)
    except ValueError:
        print("Error: Node MEM must an float")
        sys.exit(1)
        
    utility = os.getenv('UTILITY', "LGF")
    try:
        utility = str_to_utility(utility)
    except Exception as e:
        print(e)
        sys.exit(1)

    return node_id, node_name, address, port, neighbors, [cpu, gpu, mem], utility

if __name__ == '__main__':
    print("Starting Plebiscito")
    print("Reading environment variables")

    nodeId, nodeName, address, port, neighbors, resources, utility = read_env_variable()

    neighbors_ep = []
    for neighbor in neighbors:
        neighbors_ep.append(Endpoint(neighbor[0], neighbor[1], neighbor[2], neighbor[3], neighbor[4], countHop=True))

    self_ep = Endpoint(nodeName, nodeId, address, port, 10, countHop=False)
    node = PNode(id=nodeId, self_ep=self_ep, neighbors_ep=neighbors_ep, env=Environment.KUBERNETES, initial_res=resources, utility=utility)
    node.start_daemon()