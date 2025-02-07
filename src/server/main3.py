import socket

def send_message(conn, message):
    try:
        conn.sendall(message.encode())
    except Exception as e:
        print(f"Error sending message: {e}")

def receive_message(conn, buffer_size=4096, timeout=10):
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

def get_connection(server_socket, timeout=10):
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

def create_server_socket(address, family=socket.AF_INET, timeout=10):
    try:
        server_socket = socket.create_server(address, family=family)
        server_socket.settimeout(timeout)  # Set the timeout for the server socket
        server_socket.listen(2)  # Listen for 2 client (adjust as needed)
        print(f"Server listening on {address[0]}:{address[1]}")
        return server_socket
    except Exception as e:
        print(f"Error creating server socket: {e}")
        return None

def main():
    address = ("localhost", 8000)
    server_socket = create_server_socket(address)
    if not server_socket:
        return

    conn = get_connection(server_socket)
    if not conn:
        return

    message = "Hello, client!"
    send_message(conn, message)

    data = receive_message(conn)
    if data:
        print(f"Received: {data}")

    conn2 = get_connection(server_socket)
    if not conn2:
        return

    message = "Hello, client!"
    send_message(conn, message)

    data = receive_message(conn)
    if data:
        print(f"Received: {data}")

    conn2.close()
    server_socket.close()

if __name__ == "__main__":
    main()