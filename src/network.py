import json
import subprocess
import time
import requests
from requests.exceptions import ConnectionError

class CustomEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Endpoint):
            return {'name': obj.get_name(), 'ip': obj.get_IP(), 'port': obj.get_port()}
        return super().default(obj)
    
def custom_decoder(dct):
    if 'name' in dct and 'ip' in dct and 'port' in dct:
        return Endpoint(dct['name'], dct['ip'], dct['port'])
    return dct

def get_hop_count(destination_IP, destination_port):
    try:
        # Run traceroute with TCP and capture stdout
        result = subprocess.run(
            ["traceroute", "-T", destination_IP, "-p", str(destination_port)],
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,  # suppress traceroute errors
            text=True,
            check=True
        )
        
        # Count lines that start with a number (hop lines)
        hop_lines = [line for line in result.stdout.splitlines() if line.strip().split(" ")[0].isdigit()]
        return len(hop_lines)
    
    except subprocess.CalledProcessError as e:
        print(f"Error: traceroute to {destination_IP} failed.")
        raise e

class Endpoint:
    def __init__(self, node_name, node_id, ip, port, available_bw, countHop=False):
        self.__ip = ip
        self.__port = int(port)
        self.__active = True
        self.__node_name = node_name
        self.__node_id = node_id
        self.__available_bw = float(available_bw)
        self.__initial_bw = float(available_bw)
        if countHop:
            self.__hopcount = get_hop_count(self.__ip, self.__port)
        else:
            self.__hopcount = 1

    def get_available_bw(self):
        return self.__available_bw
    
    def consume_bw(self, bw):
        self.__available_bw -= bw
  
    def release_bw(self, bw):
        self.__available_bw += bw

    def get_url(self):
        return f"http://{self.__ip}:{self.__port}"
    
    def get_node_name(self):
        return self.__node_name
    
    def get_node_id(self):
        return self.__node_id
    
    def get_IP(self):
        return self.__ip
    
    def get_port(self):
        return self.__port
    
    def get_hop_count(self):
        return self.__hopcount
    
    def send_msg(self, msg):
        json_data = json.dumps(msg)
        try:
            requests.post(self.get_url(), data=json_data.encode('utf-8'))
            #print(time.time(), f"Message sent to {self.__node_name} ({self.__ip}:{self.__port})", flush=True)
            return True
        except ConnectionError as e:
            self.__active = False
            print(f"Connection error to {self.__node_name} ({self.__ip}:{self.__port}). {e}", flush=True)
            return False
        
    def request_path(self, msg):
        try:
            resp = requests.post(self.get_url() + "/path", data=msg, timeout=5)
            if resp.status_code == 200:
                return json.loads(resp.text)
            else:
                return None
        except ConnectionError as e:
            self.__active = False
            return None
        
    def was_active(self):
        return self.__active
        
    def is_active(self):
        try:
            requests.get(self.get_url() + "/status")
            return True
        except ConnectionError:
            return False
        
    def __str__(self):
        return f"{self.__node_name} ({self.__ip}:{self.__port}) Hop distance: {self.__hopcount} Available bw: {self.__available_bw}/{self.__initial_bw}"

    def __eq__(self, other):
        return self.__ip == other.__ip and self.__port == other.__port

    def __hash__(self):
        return hash((self.__ip, self.__port))

    def __repr__(self):
        return self.__str__()