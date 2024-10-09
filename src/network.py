import json
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

class Endpoint:
    def __init__(self, node_name, node_id, ip, port):
        self.__ip = ip
        self.__port = int(port)
        self.__active = True
        self.__node_name = node_name
        self.__node_id = node_id

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
    
    def send_msg(self, msg):
        json_data = json.dumps(msg)
        try:
            requests.post(self.get_url(), data=json_data.encode('utf-8'))
            return True
        except ConnectionError:
            self.__active = False
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
        return f"{self.__name} ({self.__ip}:{self.__port})"

    def __eq__(self, other):
        return self.__ip == other.__ip and self.__port == other.__port

    def __hash__(self):
        return hash((self.__ip, self.__port))

    def __repr__(self):
        return self.__str__()