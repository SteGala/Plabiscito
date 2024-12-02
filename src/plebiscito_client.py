from enum import Enum
import json
import hashlib
import time
import sys
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

jobs = []
jobs.append([0.25, 1, 1, 1, 1, 1])
jobs.append([0.25, 1, 1, 1, 1, 1])
jobs.append([0.25, 1, 1, 1, 1, 1])
jobs.append([0.25, 1, 1, 1, 1, 1])
jobs.append([0.25, 1, 1, 1, 1, 1])

jobs.append([0.25, 1, 1, 1, 1])
jobs.append([0.25, 1, 1, 1, 1])
jobs.append([0.25, 1, 1, 1, 1])
jobs.append([0.25, 1, 1, 1, 1])
jobs.append([0.25, 1, 1, 1, 1])

jobs.append([0.25, 1, 1, 1])
jobs.append([0.25, 1, 1, 1])
jobs.append([0.25, 1, 1, 1])
jobs.append([0.25, 1, 1, 1])
jobs.append([0.25, 1, 1, 1])

jobs.append([0.25, 1, 1])
jobs.append([0.25, 1, 1])
jobs.append([0.25, 1, 1])
jobs.append([0.25, 1, 1])
jobs.append([0.25, 1, 1])

if __name__ == '__main__':
    port = 0
    if len(sys.argv) == 3:
        try:
            # Read the first argument as an integer
            port = int(sys.argv[1])
            instances = int(sys.argv[2])
        except ValueError as e:
            raise e

        client = PClient("http://10.132.3.2", port, "client1")
        for i in range(instances):
            client.request_allocation(cpus=jobs[i], gpus=jobs[i], bw=jobs[i], mem=jobs[i], duration=5)
            time.sleep(5)
    else:
        print("Use with [Plebiscito port] [n_instances].") 

    
    #client.request_topology()
        