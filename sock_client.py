# import socket
# import time

# def start_client():
#     client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
#     try:
#         counter = 0
#         client_socket.connect(('127.0.0.1', 12000))
#         time.sleep(10)
#         res = client_socket.sendall("Execute".encode(), socket.MSG_WAITALL)
#         if res is not None:
#             raise Exception("Error sending message")
        
#         counter += 1
#         response = client_socket.recv(1024)
#         if response.decode() == "":
#             raise Exception("Error receiving ACK")    
        
#         counter += 1
#         print(f"Received: {response.decode()}")
    
#     except Exception as e:
#         print(f"{e}")
    
#     finally:
#         client_socket.close()
#         if counter == 2:
#             print("we're done")
#         else:
#             print("we're not done")

# if __name__ == "__main__":
#     start_client()

import time
from websockets.sync.client import connect

def hello():
    with connect("ws://localhost:12000") as websocket:
        time.sleep(10)
        websocket.send("Hello world!")
        message = websocket.recv()
        print(f"Received: {message}")

hello()