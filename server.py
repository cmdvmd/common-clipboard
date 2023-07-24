import constants
from socket import socket,  AF_INET, SOCK_STREAM
from threading import Thread


def handle_connection(conn):
    addr = conn.getsockname()[0]

    try:
        while True:
            message = conn.recv(1024)
            print(f'Received clipboard data from {addr}')

            for i, c in enumerate(clients):
                if c != conn:
                    conn.sendall(message)
                    print(f'Sent {addr} data to {c.getsockname()[0]} ({i + 1} of {len(clients) - 1})')
    except ConnectionResetError:
        clients.remove(conn)
        print(f'{addr} has disconnected')


if __name__ == '__main__':
    server = socket(AF_INET, SOCK_STREAM)
    server.bind(('', constants.PORT))
    server.listen()

    clients = []

    with server:
        while True:
            connection, _ = server.accept()
            clients.append(connection)

            print(f'{connection.getsockname()[0]} has connected')

            connection_thread = Thread(target=handle_connection, args=(connection,), daemon=True)
            connection_thread.start()
