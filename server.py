import constants
import time
from log import Log, Tag
from socket import socket, AF_INET, SOCK_STREAM, SOCK_DGRAM, SOL_SOCKET, SO_BROADCAST
from threading import Thread


def handle_connection(conn, addr):
    try:
        while True:
            data = conn.recv(1024)
            log_file.log(Tag.INFO, f'Received clipboard data from {addr}')

            for i, c in enumerate(clients):
                if c != conn:
                    c.sendall(data)
                    log_file.log(Tag.INFO, f'Sent {addr} data to {c.getpeername()[0]} ({i + 1} of {len(clients) - 1})')
    except ConnectionResetError:
        conn.close()
        clients.remove(conn)
        log_file.log(Tag.INFO, f'{addr} has disconnected')


def broadcast_ip():
    log_file.log(Tag.INFO, 'Server broadcast started')

    # Credit to ninedraft for UDP broadcasting (https://gist.github.com/ninedraft/7c47282f8b53ac015c1e326fffb664b5)
    with socket(AF_INET, SOCK_DGRAM) as broadcast_server:
        broadcast_server.settimeout(0.2)
        broadcast_server.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)

        while True:
            broadcast_server.sendto(b'universal clipboard server broadcast', ('<broadcast>', constants.BROADCAST_PORT))
            time.sleep(1)


if __name__ == '__main__':
    log_file = Log('server_log.txt')
    log_file.log(Tag.INFO, 'Server started')

    broadcast_thread = Thread(target=broadcast_ip, daemon=True)
    broadcast_thread.start()

    server = socket(AF_INET, SOCK_STREAM)
    server.bind(('', constants.PORT))
    server.settimeout(3)
    server.listen()

    clients = []

    with server:
        while True:
            try:
                connection, address = server.accept()
                clients.append(connection)

                log_file.log(Tag.INFO, f'{address[0]} has connected')

                connection_thread = Thread(target=handle_connection, args=(connection, address[0],), daemon=True)
                connection_thread.start()
            except TimeoutError:
                continue
