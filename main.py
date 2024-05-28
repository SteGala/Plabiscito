import sys
from src.plebiscito_node import PNode
from src.config import Utility
from src.network import Endpoint

if __name__ == '__main__':
    node = PNode(id=sys.argv[1], utility=Utility.LGF, self_endpoint=Endpoint("e", "localhost", sys.argv[2]), neighbors_endpoint=[Endpoint("e", "localhost", sys.argv[3])])
    node.start_daemon()