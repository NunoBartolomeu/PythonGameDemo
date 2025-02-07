import socket

SERVER_IP = "82.154.104.161"
PORT = 47624

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((SERVER_IP, PORT))

def listen():
    while True:
        try:
            message = client.recv(1024).decode()
            if not message:
                break
            print(f"{message}")
        except:
            break

import threading
threading.Thread(target=listen, daemon=True).start()

while True:
    msg = input("You: ")
    client.sendall(msg.encode())




'''
Turn: {player_name, pieces[]}
Piece: {number, actions[]}
Action: {type, SPECIFICS}
    MoveAction: {MOVE, from, to}
    BreakAction: {BREAK, wall_position}

    

Conectar ao servidor mandas o nome do jogador
O servidor manda a visão do jogador
O cliente apresenta a visão do jogador
O jogador faz o seu turno
O cliente manda o turno para o servidor
O servidor aplica o turno
O servidor manda a visão do jogador
'''

