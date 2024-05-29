import json
import requests


class Endpoint:
    def __init__(self, name, ip, port):
        self.__name = name
        self.__ip = ip
        self.__port = int(port)

    def get_url(self):
        return f"http://{self.__ip}:{self.__port}"
    
    def get_IP(self):
        return self.__ip
    
    def get_port(self):
        return self.__port
    
    def send_msg(self, msg):
        json_data = json.dumps(msg)
        _ = requests.post(self.get_url(), data=json_data.encode('utf-8'))
        
    def __str__(self):
        return f"{self.__name} ({self.__ip}:{self.__port})"

    def __eq__(self, other):
        return self.__ip == other.__ip and self.__port == other.__port

    def __hash__(self):
        return hash((self.__ip, self.__port))

    def __repr__(self):
        return self.__str__()