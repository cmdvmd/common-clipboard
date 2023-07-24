import sys
import win32clipboard as clipboard
import time
import constants
from socket import socket, AF_INET, SOCK_STREAM, gethostname, gethostbyname
from threading import Thread


def send_message(message):
    client.sendall(message.encode())


def get_copied_data():
    for fmt in formats:
        try:
            clipboard.OpenClipboard()
            return clipboard.GetClipboardData(fmt)
        except TypeError:
            continue
        finally:
            clipboard.CloseClipboard()
    else:
        print('Unknown copied data', file=sys.stderr)
        # raise TypeError('Unknown copied data')


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
        clipboard.SetClipboardData(inverse_formats['Text'], copied_data.decode())
        clipboard.CloseClipboard()


# formats = {clipboard.CF_UNICODETEXT: 'Text', clipboard.CF_DIB: 'Image'}
formats = {clipboard.CF_UNICODETEXT: 'Text'}
inverse_formats = {v: k for k, v in formats.items()}

current_data = get_copied_data()
client = socket(AF_INET, SOCK_STREAM)

if __name__ == '__main__':
    client.connect(('localhost', constants.PORT))

    try:
        listener_thread = Thread(target=listen_for_changes, daemon=True)
        listener_thread.start()
        detect_new_copy()
    except KeyboardInterrupt:
        pass
    finally:
        client.close()
