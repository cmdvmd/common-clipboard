import requests
import time
import win32clipboard as clipboard
from log import Log, Tag
from socket import gethostbyname, gethostname
from threading import Thread
from infi.systray import SysTrayIcon


def test_server_ip(index):
    global server_url

    try:
        if not server_url:
            tested_url = f'http://{base_ipaddr}.{index}:{server_port}'

            response = requests.post(tested_url + '/register', json={'name': gethostname()})
            assert response.ok

            server_url = tested_url
    except (requests.exceptions.ConnectionError, AssertionError):
        return


def find_server():
    global server_url

    systray.update(hover_text='Common Clipboard: Not Connected')

    server_url = ''
    while not server_url:
        for i in range(1, 255):
            test_url_thread = Thread(target=test_server_ip, args=(i,), daemon=True)
            test_url_thread.start()
        time.sleep(finding_server_delay)

    systray.update(hover_text='Common Clipboard: Connected')
    log_file.log(Tag.INFO, f'Server found: {server_url}')


def get_copied_data():
    try:
        clipboard.OpenClipboard()
        data = clipboard.GetClipboardData(clipboard.CF_UNICODETEXT)
        return data
    except TypeError:
        log_file.log(Tag.ERROR, 'Invalid copied data format')
    finally:
        clipboard.CloseClipboard()


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
        if server_url:
            try:
                data_request = requests.get(server_url + '/clipboard')
                if data_request.ok:
                    copied_data = data_request.json()['data']
                    if copied_data != current_data:
                        log_file.log(Tag.INFO, 'New clipboard data has been received')
                        current_data = copied_data
                        clipboard.OpenClipboard()
                        clipboard.EmptyClipboard()
                        clipboard.SetClipboardData(clipboard.CF_UNICODETEXT, copied_data)
                        clipboard.CloseClipboard()
                else:
                    log_file.log(Tag.ERROR, 'Invalid response from server')
            except requests.exceptions.ConnectionError:
                log_file.log(Tag.ERROR, 'Lost connection to server')
                find_server()
        time.sleep(listener_delay)


if __name__ == '__main__':
    server_port = 5000
    finding_server_delay = 1
    listener_delay = 0.3
    log_file = Log('client_log.txt')

    server_url = ''
    ipaddr = gethostbyname(gethostname())
    base_ipaddr = '.'.join(ipaddr.split('.')[:-1])
    current_data = get_copied_data()

    systray = SysTrayIcon('static/systray_icon.ico', 'Common Clipboard')
    systray.start()

    log_file.log(Tag.INFO, 'Starting search for server')

    finder_thread = Thread(target=find_server, daemon=True)
    finder_thread.start()

    listener_thread = Thread(target=listen_for_changes, daemon=True)
    listener_thread.start()
    detector_thread = Thread(target=detect_new_copy, daemon=True)
    detector_thread.start()
