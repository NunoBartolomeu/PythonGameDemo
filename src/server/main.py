import socket
import threading
import json
import time
from types import SimpleNamespace
from gen_game import generate_game
from logic import apply_turn
import select

import signal
import sys

sys.path.append("../")
from common.dto import PlayerInfoDTO, board_to_json
from utils.serialization.serialize_board import BoardEncoder
from utils.serialization.serialize_player_turn import as_player_turn

IP_ADDRESS = "localhost"
IP_PORT = 8000

NUM_PLAYERS = 1
BOARD_WIDTH = 10
BOARD_HEIGHT = 50

class Lobby:
    def __init__(self):
        self.players = {}
        self.conn = []

    def add_player(self, conn, player_info):
        player_name = player_info["name"]
        player_color = player_info["color"]
        self.players[conn] = PlayerInfoDTO(player_name, player_color)
        print(f"Player {player_name} added with color {player_color}")

    def add_connection(self, conn):
        self.conn.append(conn)
        print(f"Connection added: {conn}")

    def send_to_all(self, message):
        for conn in self.conn:
            send_message(conn, message)
    
    def get_player_infos(self):
        return list(self.players.values())

#################################### Comunication ####################

def create_server_socket(address, num_players, timeout):
    try:
        server_socket = None
        if socket.has_dualstack_ipv6():
            server_socket = socket.create_server(address, family = socket.AF_INET6, dualstack_ipv6 = True)
        else:
            server_socket = socket.create_server(address, family = socket.AF_INET)
        server_socket.settimeout(timeout)
        server_socket.listen(num_players)  
        print(f"Server listening on {address[0]}:{address[1]}")
        return server_socket
    except Exception as e:
        print(f"Error creating server socket: {e}")
        return None
    
def get_connection(server_socket, timeout):
    try:
        server_socket.settimeout(timeout)  # Set the timeout for accepting connections
        conn, addr = server_socket.accept()
        print(f"Connection established with {addr}")
        return conn
    except socket.timeout:
        print(f"Timeout waiting for a connection.")
        return None
    except Exception as e:
        print(f"Error accepting connection: {e}")
        return None

def receive_message(conn, buffer_size=(1 * 10 ** 9), timeout=10):
    try:
        conn.settimeout(timeout)  # Set the timeout here
        data = conn.recv(buffer_size).decode()
        if not data:
            return None
        return data
    except socket.timeout:
        print("Timeout waiting for message.")
        return None
    except Exception as e:
        print(f"Error receiving message: {e}")
        return None

def send_message(conn, message):
    try:
        conn.sendall(message.encode())
        #print(f"Sent message: {message}")
    except Exception as e:
        print(f"Error sending message: {e}")


################################# Send data ####################

def send_all_boards(lobby, players):
    for conn in lobby.conn:
        for player in players:
            if player.name == lobby.players[conn].name:
                send_board(conn, player.board)
                break
    print("Boards sent.")

def send_board(conn, board):
    send_message(conn, json.dumps(board, cls = BoardEncoder))

def send_num_players(conn, num_players):
    send_message(conn, num_players.__str__())

def send_player_infos(conn, player_infos):
    player_infos_dicts = [player.__dict__ for player in player_infos]  # Convert objects to dicts
    send_message(conn, json.dumps(player_infos_dicts))


################################ Receive data ####################

def receive_player_info(conn):
    data = receive_message(conn)
    if data:
        player_info = json.loads(data)
        print("Received player info.")
        return player_info

def receive_turn(conn):
    data = receive_message(conn)
    print(data)
    return json.loads(data, object_hook = as_player_turn)

################################ Main ####################

def main():
    address = (IP_ADDRESS, IP_PORT)
    server_socket = create_server_socket(address, NUM_PLAYERS, 100)
    lobby = Lobby()

    while len(lobby.players) < NUM_PLAYERS:
        ready_to_read, _, _ = select.select([server_socket] + lobby.conn, [], [], 1)
        for sock in ready_to_read:
            if sock is server_socket:
                conn = get_connection(server_socket, 100)
                if conn:
                    lobby.add_connection(conn)
                    send_num_players(conn, NUM_PLAYERS)
            else:
                conn = sock
                player_info = receive_player_info(conn)
                print(f"Received player info: {player_info}")
                lobby.add_player(conn, player_info)
                for conn in lobby.conn:
                    send_player_infos(conn, lobby.get_player_infos())

    board, players = generate_game(lobby.get_player_infos(), BOARD_WIDTH, BOARD_HEIGHT)
    print("Game generated.")
    send_all_boards(lobby, players)

    turns = []
    while True:
        ready_to_read, _, _ = select.select(lobby.conn, [], [], 1)
        for conn in ready_to_read:
            turn = receive_turn(conn)
            turns.append(turn)
            if len(turns) == NUM_PLAYERS:
                apply_turn(board, players, turns)
                turns = []
                send_all_boards(lobby, players)

if __name__ == "__main__":
    main()