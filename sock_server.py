# import socket
# import threading
# import time

# def handle_client_connection(client_socket):
#     try:
#         counter = 0
#         message = client_socket.recv(1024)
#         if message.decode() == "":
#             raise Exception("Error receiving Execute")    
        
#         counter += 1
#         print(f"Received: {message.decode()}")
        
#         # time.sleep(10)
        
#         # res = client_socket.send("Ack".encode(), socket.MSG_WAITALL)
#         # if res == 0:
#         #     raise Exception("Error sending ACK")
        
#         counter += 1
    
#     except Exception as e:
#         print(f"{e}")
    
#     finally:
#         client_socket.close()
#         if counter == 2:
#             print("we're done")
#         else:
#             print("we're not done")

# def start_server():
#     server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#     server_socket.bind(('0.0.0.0', 13001))
#     server_socket.listen(5)
#     print("Server listening on port 13001")
    
#     while True:
#         client_socket, addr = server_socket.accept()
#         print(f"Accepted connection from {addr}")
#         handle_client_connection(client_socket)

# if __name__ == "__main__":
#     start_server()

import asyncio
from websockets.server import serve

async def echo(websocket):
    async for message in websocket:
        await websocket.send(message)

async def main():
    async with serve(echo, "localhost", 13001):
        await asyncio.Future()  # run forever

asyncio.run(main())