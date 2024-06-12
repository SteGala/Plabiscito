import sys
from src.plebiscito_node import PNode
from src.config import Utility
from src.network import Endpoint

if __name__ == '__main__':
    if len(sys.argv) < 4:
        sys.exit("Usage: python3 main.py <node_id> <self_ip> <self_port> ...")

    self_ep = Endpoint(sys.argv[1], sys.argv[2], sys.argv[3])
    neighbors_ep = []
    i = 4
    while True:
        if i >= len(sys.argv):
            break
        neighbors_ep.append(Endpoint(sys.argv[i], sys.argv[i+1], sys.argv[i+2]))
        i += 3

    node = PNode(id=sys.argv[1], utility=Utility.LGF, self_ep=self_ep, neighbors_ep=neighbors_ep)
    node.start_daemon()