from enum import Enum
import json
import hashlib
import time

import requests
from datetime import datetime

class PClient:
    def __init__(self, host, port, client_id):
        self.__host = host
        self.__port = port
        self.__client_id = client_id

    def request_topology(self, timeout=2):
        timestamp_str = datetime.now().isoformat() 
        hash_object = hashlib.sha256(timestamp_str.encode('utf-8'))
        hash_hex = hash_object.hexdigest()
        job_id = hash_hex[:10]
        print(f"Job ID: {job_id}")

        msg = {
            "type": "topology",
            "job_id": job_id,
            "user": self.__client_id,
            "duration": 0,
            "edge_id": None,
        }
        json_data = json.dumps(msg)
        _ = requests.post(self.__host + ":" + str(self.__port), data=json_data.encode('utf-8'))

    def request_allocation(self, cpus=[], gpus=[], bw=[], mem=[], min_bundle=0, max_bundle=10000, duration=1, timeout=2):       
        if not (len(cpus) == len(gpus) == len(bw) == len(mem)):
            print("The resource arrays must be of the same lenght!")
            return
        
        timestamp_str = datetime.now().isoformat() 
        hash_object = hashlib.sha256(timestamp_str.encode('utf-8'))
        hash_hex = hash_object.hexdigest()
        job_id = hash_hex[:10]
        print(f"Job ID: {job_id}")
        
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

        return job_id

if __name__ == '__main__':
    client = PClient("http://192.168.11.95", 30000, "client1")
    client.request_allocation(cpus=[1, 1, 1], gpus=[1, 1, 1], bw=[1, 1, 1], mem=[1, 1, 1], duration=5)
    client.request_topology()
        