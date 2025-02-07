import socket
import threading
import json
from types import SimpleNamespace
from base_classes import Board, Player, ActionType
from turn_logic import update_player_board, remove_ghost_pieces, resolve_duels
from board_gen import BOARD_WIDTH, BOARD_HEIGHT, generate_game
from draw_config import handle_click

server_socket = None
clients = {}

def start_server(address, num_players = 2, board_width = BOARD_WIDTH, board_height = BOARD_HEIGHT):
    if socket.has_dualstack_ipv6():
        server_socker = socket.create_server(address, family = socket.AF_INET6, dualstack_ipv6 = True)
    else:
        server_socker = socket.create_server(address, family = socket.AF_INET)
    server_socker.listen(num_players)
    threading.Thread(target = lobby, args = (num_players)).start()

def lobby(num_players):
    print("Waiting for players to join.")
    while len(clients) < num_players:
        conn, _ = server_socket.accept()
        threading.Thread(target = getPlayerName, args = (conn)).start()

    print("All players joined, starting game.")
    for client in clients:
        for player in players:
            if player.name in clients.keys():
                threading.Thread(target = handle_player, args = (player)).start()
                break
        
        threading.Thread(target = start_game).start

def start_game():
    print("Game started.")
    board_state, players = generate_game(clients.keys())

    while True:
        threads = []
        for player in players:
            if player.name in clients.keys():
                thread = threading.Thread(target = handle_player, args = (board_state, player))
                thread.start()
                threads.append(thread)
                break

        for thread in threads:
            thread.join()

        resolve_duels(board_state)
        remove_ghost_pieces(board_state)
        for player in players:
            update_player_board(player, board_state)
        
        if check_loss(players):
            game_end()
            break

def getPlayerName(conn):
    conn.sendall("Please enter player name.")
    name = conn.recv(1024).decode().strip()
    if not name:
        conn.sendall("Need a name to play.")
        print("A player did not put a name.")
        conn.close()
        return
    clients[name] = conn
    print(f"Player {name} has joined the game.")

def handle_player(board, player):
    conn = clients[player.name]
    conn.sendall(json.dumps(player.board.__dict__).encode())

    while True:
        player_actions = conn.recv()
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

def check_loss(players):
    have_lost = []

    for player in players:
        have_lost.append(len(player.board.get_pieces()) == 0)

    if have_lost <= 1:
        won = players[have_lost.indexOf(True)]
        message = f'Player {won.name} has won.'
        print(message)
        for client in clients.values():
            client.sendall(message)
        return True

    return False

def game_end():
    server_socket.close()
