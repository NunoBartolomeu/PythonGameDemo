import socket
import threading
import json
from types import SimpleNamespace

def connect_to_server(address):
    client_socket = socket.create_connection(address)
    print("Connected to server.")
    print("Awaiting for name request.")
    while True:
        request = client_socket.recv(4096)
        if request:
            print(f"{request.decode()}")
            return client_socket

def await_result(client_socket):
    while True:
        result = client_socket.recv(4096)
        if result:
            board_view = result.decode()
            print(f"Player board received: {board_view}")
            return json.loads(board_view, object_hook = lambda d: SimpleNamespace(**d))

def send_actions(client_socket, player_actions):
    client_socket.sendall(json.dumps(player_actions.__dict__).encode())
    print("Sent player actions to server.")

def send_name(client_socket, name):
    client_socket.sendall(name.encode())
    print("Sent player name to server.")

def main():
    client_socket = connect_to_server(("127.0.0.1", 8000))
    send_name(client_socket, "Name3")

if __name__ == "__main__":
    main()
