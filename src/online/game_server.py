import socket
import threading
import json
from types import SimpleNamespace
from base_classes import Board, Player, ActionType
from turn_logic import update_player_board, remove_ghost_pieces, resolve_duels
from board_gen import BOARD_WIDTH, BOARD_HEIGHT, generate_game
from draw_config import handle_click
from utils.serialization.serialize_board import BoardEncoder

def start_server(address, num_players = 2, board_width = BOARD_WIDTH, board_height = BOARD_HEIGHT):
    server_socket = None
    if socket.has_dualstack_ipv6():
        server_socket = socket.create_server(address, family = socket.AF_INET6, dualstack_ipv6 = True)
    else:
        server_socket = socket.create_server(address, family = socket.AF_INET)
    server_socket.listen(num_players)
    print(f'Server listening on port {address[1]}...')
    threading.Thread(target = lobby, args = (num_players, server_socket, board_width, board_height)).start()

def lobby(num_players, server_socket, board_width, board_height):
    print("Waiting for players to join.")
    clients = {}
    threads = []
    while len(threads) < num_players:
        conn, _ = server_socket.accept()
        thread = threading.Thread(target = getPlayerName, args = (conn, clients))
        thread.start()
        threads.append(thread)

    for thread in threads:
        thread.join()

    print("All players joined, starting game.")
    threading.Thread(target = start_game, args = (server_socket, clients, board_width, board_height)).start()

def start_game(server_socket, clients, board_width, board_height):
    print("Game started.")
    board_state, players = generate_game(clients.keys(), 10, 10)

    while True:
        threads = []
        for player in players:
            if player.name in clients.keys():
                thread = threading.Thread(target = handle_player, args = (board_state, player, clients))
                thread.start()
                threads.append(thread)

        for thread in threads:
            thread.join()

        resolve_duels(board_state)
        remove_ghost_pieces(board_state)
        for player in players:
            update_player_board(player, board_state)

        if check_loss(board_state, players, clients):
            game_end(server_socket)
            break

def getPlayerName(conn, clients):
    conn.sendall("Please enter player name.".encode())
    name = conn.recv(4096).decode().strip()
    if not name:
        conn.sendall("Need a name to play.".encode())
        print("A player did not put a name.")
        conn.close()
        return
    #if clients[name]:
     #   print(f"Player {name} has already joined.")
    #    return
    clients[name] = conn
    #conn.sendall("Joined game.".encode())
    print(f"Player {name} has joined the game.")

def handle_player(board, player, clients):
    conn = clients[player.name]

    conn.sendall(json.dumps(player.board, cls = BoardEncoder).encode())

    while True:
        player_actions = conn.recv(4096)
        if player_actions:
            player_actions = json.loads(player_actions.decode(), object_hook = lambda d: SimpleNamespace(**d))
            print(f'Player {player.name} has made actions: {player_actions}')
            break

    handle_player_actions(board, player_actions)

def handle_player_actions(board, player_actions):
    selected_piece = None

    for piece_action in player_actions.pieces:
        for action in piece_action.actions:
            if action.type == ActionType.MOVE:
                selected_piece = board.get_piece(action.start[0], action.start[1])
                handle_click(board, action.end[0], action.end[1], selected_piece)

def check_loss(board, players, clients):
    have_lost = []

    for player in players:
        have_lost.append(len(board.get_pieces(player, False)) != 0)
    print(have_lost)

    if sum(have_lost) <= 1:
        won = players[have_lost.index(True)]
        message = f'Player {won.name} has won.'
        print(message)
        for client in clients.values():
            client.sendall(message.encode())
        return True

    return False

def game_end(server_socket):
    server_socket.close()

def main():
    start_server(("localhost", 8000))

if __name__ == "__main__":
    main()
