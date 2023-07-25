import win32clipboard as clipboard
import time
import constants
from enum import Enum
from log import Log, Tag
from socket import socket, AF_INET, SOCK_STREAM, SOCK_DGRAM, SOL_SOCKET, SO_BROADCAST
from threading import Thread


class Format(Enum):
    TEXT = clipboard.CF_UNICODETEXT
    # IMAGE = clipboard.CF_DIB
    # FILE = clipboard.CF_HDROP


def find_server():
    global client

    client = socket(AF_INET, SOCK_STREAM)

    # Credit to ninedraft for UDP broadcasting (https://gist.github.com/ninedraft/7c47282f8b53ac015c1e326fffb664b5)
    with socket(AF_INET, SOCK_DGRAM) as broadcast_client:
        broadcast_client.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)

        broadcast_client.bind(('', constants.BROADCAST_PORT))
        _, addr = broadcast_client.recvfrom(1024)

        client.connect((addr[0], constants.PORT))
        log_file.log(Tag.INFO, f'Connected to server: {addr[0]}')


def get_copied_data():
    for fmt in list(Format):
        try:
            clipboard.OpenClipboard()
            data = clipboard.GetClipboardData(fmt.value)
            if fmt == Format.TEXT:
                data = data.encode()
            return data
        except TypeError:
            continue
        finally:
            clipboard.CloseClipboard()
    else:
        log_file.log(Tag.ERROR, 'Unknown data format')


def detect_new_copy():
    global current_data

    while True:
        new_data = get_copied_data()

        if new_data != current_data:
            current_data = new_data
            client.sendall(new_data)
        time.sleep(0.3)


def listen_for_changes():
    global current_data

    try:
        while True:
            copied_data = client.recv(1024)

            log_file.log(Tag.INFO, 'Received new copy data from server')

            clipboard.OpenClipboard()
            clipboard.EmptyClipboard()
            clipboard.SetClipboardData(Format.TEXT.value, copied_data.decode())
            clipboard.CloseClipboard()

            current_data = copied_data
    except ConnectionResetError:
        log_file.log(Tag.ERROR, 'Lost connection to server')
        client.close()
        find_server()


if __name__ == '__main__':
    log_file = Log('client_log.txt')

    client = socket()
    current_data = get_copied_data()

    find_server()

    try:
        listener_thread = Thread(target=listen_for_changes, daemon=True)
        listener_thread.start()
        detect_new_copy()
    except KeyboardInterrupt:
        pass
    finally:
        client.close()
