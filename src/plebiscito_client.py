from enum import Enum

import requests


class PClient:
    def __init__(self, host, port, client_id):
        self.__host = host
        self.__port = port
        self.__client_id = client_id

    def request_topology(self, ):
        msg = {}
        msg["type"] = "topology"
        msg[]
        _ = requests.post(self.get_url(), data=msg)