import requests
import time
import win32clipboard as clipboard
import atexit
from log import Log, Tag
from socket import gethostbyname, gethostname
from threading import Thread
from enum import Enum


class Format(Enum):
    TEXT = clipboard.CF_UNICODETEXT
    # IMAGE = clipboard.CF_DIB
    # FILE = clipboard.CF_HDROP


def test_server_ip(index):
    global server_url

    try:
        if not server_url:
            tested_url = f'http://{base_ipaddr}.{index}:{server_port}'

            response = requests.post(tested_url + '/register', json={'name': gethostname(), 'ipaddr': ipaddr})
            assert response.ok

            server_url = tested_url
    except (requests.exceptions.ConnectionError, AssertionError):
        pass


def find_server():
    global server_url

    server_url = ''
    while not server_url:
        for i in range(1, 255):
            test_url_thread = Thread(target=test_server_ip, args=(i,), daemon=True)
            test_url_thread.start()
        time.sleep(finding_server_delay)

    log_file.log(Tag.INFO, f'Server found: {server_url}')


@atexit.register
def disconnect():
    if server_url:
        requests.post(server_url + '/remove', json={'ipaddr': ipaddr})
        log_file.log(Tag.INFO, 'Disconnected from server')


def get_copied_data():
    for fmt in list(Format):
        try:
            clipboard.OpenClipboard()
            data = clipboard.GetClipboardData(fmt.value)
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

        if server_url and new_data != current_data:
            log_file.log(Tag.INFO, 'New data copied on local machine')
            current_data = new_data
            requests.post(server_url + '/clipboard', json={'data': new_data})
        time.sleep(listener_delay)


def listen_for_changes():
    global current_data

    while True:
        try:
            data_request = requests.get(server_url + '/clipboard')

            if data_request.ok:
                copied_data = data_request.json()['data']
                if copied_data != current_data:
                    log_file.log(Tag.INFO, 'New clipboard data has been received')
                    current_data = copied_data
                    clipboard.OpenClipboard()
                    clipboard.EmptyClipboard()
                    clipboard.SetClipboardData(Format.TEXT.value, copied_data)
                    clipboard.CloseClipboard()
            else:
                log_file.log(Tag.ERROR, 'Invalid response from server')
            time.sleep(listener_delay)
        except requests.exceptions.ConnectionError:
            log_file.log(Tag.ERROR, 'Lost connection to server')
            find_server()


if __name__ == '__main__':
    server_port = 5000
    finding_server_delay = 1
    listener_delay = 0.3
    log_file = Log('client_log.txt')

    server_url = ''
    ipaddr = gethostbyname(gethostname())
    base_ipaddr = '.'.join(ipaddr.split('.')[:-1])
    current_data = get_copied_data()

    log_file.log(Tag.INFO, 'Starting search for server')
    find_server()

    try:
        listener_thread = Thread(target=listen_for_changes, daemon=True)
        listener_thread.start()
        detect_new_copy()
    except KeyboardInterrupt:
        pass
