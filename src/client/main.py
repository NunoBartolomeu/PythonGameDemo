import pygame
import socket
import json
import select
import sys

from drawing import draw_welcome_page, draw_waiting_page

sys.path.append("../")
from common.dto import PlayerInfoDTO

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

def receive_message(conn, buffer_size=4096):
    try:
        data = conn.recv(buffer_size).decode()
        if data:
            print(f"Received message: {data}")
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

################################# 

def main():
    client_socket = connect_to_server(("localhost", 8000))
    num_players = receive_num_players(client_socket)

    pygame.init()
    screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    page = "welcome"

    input_text = ""
    rgb = [128, 128, 128]
    selected_channel = 0  # 0 for R, 1 for G, 2 for B

    while page=="welcome":
        draw_welcome_page(screen, input_text, rgb, selected_channel)
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return

                elif page == "welcome":
                    if event.key == pygame.K_RETURN:
                        if input_text:
                            player_info = PlayerInfoDTO(input_text, tuple(rgb))
                            send_message(client_socket, json.dumps(player_info.__dict__))
                            page = "waiting"
                    elif event.key == pygame.K_BACKSPACE:
                        input_text = input_text[:-1]
                    elif event.key == pygame.K_TAB:
                        selected_channel = (selected_channel + 1) % 3
                    elif event.key in [pygame.K_UP, pygame.K_DOWN]:
                        change = 10 if event.key == pygame.K_UP else -10
                        rgb[selected_channel] = max(0, min(255, rgb[selected_channel] + change))
                    elif len(input_text) < 20 and event.unicode.isalnum():
                        input_text += event.unicode
    
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

    while page=="game":
        print("Game page not implemented yet.")
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
        return
    
if __name__ == "__main__":
    main()
    pygame.quit()