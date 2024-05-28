from enum import Enum
import json
import random
import time
import numpy as np

import requests


class PClient:
    def __init__(self, host, port, client_id):
        self.__host = host
        self.__port = port
        self.__client_id = client_id

    def request_topology(self, timeout=2):
        msg = {}
        msg["type"] = "topology"
        _ = requests.post(self.get_url(), data=msg)

    def request_allocation(self, job_id, cpus=[], gpus=[], bw=[], mem=[], min_bundle=0, max_bundle=10000, duration=1, timeout=2):       
        if not (len(cpus) == len(gpus) == len(bw) == len(mem)):
            print("The resource arrays must be of the same lenght!")
            return
        
        data = {
            "type": "allocate", 
            "job_id": job_id,
            "user": self.__client_id,
            "duration": duration,
            "Bundle_size": len(cpus),
            "Bundle_min": min_bundle, # Do not change!! This could be either 1 or = to N_layer_max
            "Bundle_max": max_bundle,
            "edge_id": None,
            "Bundle_gpus": gpus,
            "Bundle_cpus": cpus,
            "Bundle_memory": mem,
            "Bundle_bw": bw,
            }
        
        json_data = json.dumps(data)

        _ = requests.post(self.__host + ":" + str(self.__port), data=json_data.encode('utf-8'))

if __name__ == '__main__':
    client = PClient("http://localhost", 9090, "client1")
    client.request_allocation(job_id="1", cpus=[1], gpus=[0], bw=[0], mem=[0], duration=5)
        