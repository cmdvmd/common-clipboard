import constants
from log import Log, Tag
from socket import socket,  AF_INET, SOCK_STREAM
from threading import Thread


def handle_connection(conn):
    addr = conn.getsockname()[0]

    try:
        while True:
            message = conn.recv(1024)
            log_file.log(Tag.INFO, f'Received clipboard data from {addr}')

            for i, c in enumerate(clients):
                if c != conn:
                    conn.sendall(message)
                    log_file.log(Tag.INFO, f'Sent {addr} data to {c.getsockname()[0]} ({i + 1} of {len(clients) - 1})')
    except ConnectionResetError:
        clients.remove(conn)
        log_file.log(Tag.INFO, f'{addr} has disconnected')


if __name__ == '__main__':
    server = socket(AF_INET, SOCK_STREAM)
    server.bind(('', constants.PORT))
    server.settimeout(3)
    server.listen()

    log_file = Log('server_log.txt')

    log_file.log(Tag.INFO, 'Server started')

    clients = []

    while True:
        try:
            connection, _ = server.accept()
            clients.append(connection)

            log_file.log(Tag.INFO, f'{connection.getsockname()[0]} has connected')

            connection_thread = Thread(target=handle_connection, args=(connection,), daemon=True)
            connection_thread.start()
        except TimeoutError:
            continue

    server.close()
