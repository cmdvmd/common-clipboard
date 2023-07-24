import sys
import win32clipboard as clipboard
import time
import constants
from enum import Enum
from log import Log, Tag
from socket import socket, AF_INET, SOCK_STREAM
from threading import Thread


class Format(Enum):
    TEXT = clipboard.CF_UNICODETEXT
    # IMAGE = clipboard.CF_DIB
    # FILE = clipboard.CF_HDROP


def send_message(message):
    client.sendall(message.encode())


def get_copied_data():
    for fmt in list(Format):
        try:
            clipboard.OpenClipboard()
            return clipboard.GetClipboardData(fmt.value)
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
            send_message(new_data)
        time.sleep(0.3)


def listen_for_changes():
    while True:
        copied_data = client.recv(1024)

        clipboard.OpenClipboard()
        clipboard.SetClipboardData(Format.TEXT, copied_data.decode())
        clipboard.CloseClipboard()


if __name__ == '__main__':
    current_data = get_copied_data()
    client = socket(AF_INET, SOCK_STREAM)
    client.connect(('localhost', constants.PORT))

    log_file = Log('client_log.txt')

    try:
        listener_thread = Thread(target=listen_for_changes, daemon=True)
        listener_thread.start()
        detect_new_copy()
    except KeyboardInterrupt:
        pass
    finally:
        client.close()
