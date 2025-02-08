import pygame
import socket
import json
import select
import sys

from drawing import draw_welcome_page, draw_waiting_page, draw_board, draw_possible_moves, draw_gameover, TILE_SIZE
from common.dto import PlayerInfoDTO
from utils.serialization.serialize_board import as_board
from utils.serialization.serialize_player_turn import PlayerTurnEncoder
from common.base_classes import PlayerTurn
from logic import move_piece, break_wall


def connect_to_server(address):
    client_socket = socket.create_connection(address)
    print("Connected to server.")
    return client_socket

def send_message(conn, message):
    try:
        conn.sendall(message.encode())
        print(f"Sent message: {message}")
    except Exception as e:
        print(f"Error sending message: {e}")

def receive_message(conn, buffer_size=(1 * 10 ** 9)):
    try:
        data = conn.recv(buffer_size).decode()
        if data:
            #print(f"Received message: {data}")
            return data
    except Exception as e:
        print(f"Error receiving message: {e}")
        return None

################################

def receive_players(client_socket):
    data = receive_message(client_socket)
    if data:
        players = [PlayerInfoDTO(**player) for player in json.loads(data)]
        print("Received players list from server.")
        return players

def receive_num_players(client_socket):
    data = receive_message(client_socket)
    if data:
        num_players = int(data)
        print(f"Received number of players: {num_players}")
        return num_players

def receive_player_board(client_socket):
    data = receive_message(client_socket)
    print("Board received.")
    return json.loads(data, object_hook = as_board)

def send_turn(client_socket, turn):
    send_message(client_socket, json.dumps(turn, cls = PlayerTurnEncoder))

################################# 

def main():
    client_socket = connect_to_server(("localhost", 8000))
    num_players = receive_num_players(client_socket)

    pygame.init()
    screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    page = "welcome"

    player_name = ""
    rgb = [128, 128, 128]
    selected_channel = 0  # 0 for R, 1 for G, 2 for B

    while page=="welcome":
        draw_welcome_page(screen, player_name, rgb, selected_channel)
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return

                elif page == "welcome":
                    if event.key == pygame.K_RETURN:
                        if player_name:
                            player_info = PlayerInfoDTO(player_name, tuple(rgb))
                            send_message(client_socket, json.dumps(player_info.__dict__))
                            page = "waiting"
                    elif event.key == pygame.K_BACKSPACE:
                        player_name = player_name[:-1]
                    elif event.key == pygame.K_TAB:
                        selected_channel = (selected_channel + 1) % 3
                    elif event.key in [pygame.K_UP, pygame.K_DOWN]:
                        change = 10 if event.key == pygame.K_UP else -10
                        rgb[selected_channel] = max(0, min(255, rgb[selected_channel] + change))
                    elif len(player_name) < 20 and event.unicode.isalnum():
                        player_name += event.unicode

    players = []

    while page=="waiting":
        ready_to_read, _, _ = select.select([client_socket], [], [], 1)
        if client_socket in ready_to_read:
            players = receive_players(client_socket)
            if len(players) == num_players:
                page = "game"

        draw_waiting_page(screen, players, num_players)
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return

    board = receive_player_board(client_socket)
    turn = PlayerTurn(player_name)
    selected_piece = None

    while page=="game":
        draw_board(screen, board)
        if selected_piece:
            draw_possible_moves(screen, board, selected_piece)
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return

            elif event.type == pygame.MOUSEBUTTONDOWN:
                x, y = event.pos[1] // TILE_SIZE, event.pos[0] // TILE_SIZE
                clicked_tile = board.get_tile(x, y)
                if not selected_piece:
                    for piece in clicked_tile.pieces:
                        if not piece.is_ghost:
                            selected_piece = piece
                else:
                    if clicked_tile.is_floor():
                        has_moved = move_piece(board, selected_piece, x, y)
                        if has_moved:
                            turn.add_move_action(selected_piece, (x, y))
                    else:
                        has_broken_wall = break_wall(board, selected_piece, x, y)
                        if has_broken_wall:
                            turn.add_break_action(selected_piece, (x, y))
                    selected_piece = None

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    send_turn(client_socket, turn)
                    board = receive_player_board(client_socket)
                    turn.clear_actions()
                    if board.gameover:
                        page = "gameover"

    while page == "gameover":
        draw_gameover(screen)
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return

if __name__ == "__main__":
    main()
    pygame.quit()