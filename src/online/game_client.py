import socket
import threading
import json
from types import SimpleNamespace

client_socket = None

def connect_to_server(address):
    client_socket = socket.create_connection(address)
    print("Connected to server.")
    print("Awaiting for name request.")
    while True:
        request = client_socket.recv()
        if request:
            print(f"{request.decode()}")
            break

def await_result():
    while True:
        result = client_socket.recv()
        if result:
            board_view = result.decode()
            print(f"Player board received: {board_view}")
            return json.loads(board_view, object_hook = lambda d: SimpleNamespace(**d))

def send_actions(player_actions):
    client_socket.sendall(json.dumps(player_actions.__dict__).encode())
    print("Sent player actions to server.")

def send_name(name):
    client_socket.sendall(name.encode())
    print("Sent player name to server.")
