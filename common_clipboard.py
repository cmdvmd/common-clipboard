import requests
import time
import win32clipboard as clipboard
from log import Log, Tag
from socket import gethostbyname, gethostname
from threading import Thread
from enum import Enum
from infi.systray import SysTrayIcon
from io import BytesIO


class Format(Enum):
    TEXT = clipboard.CF_TEXT
    IMAGE = clipboard.RegisterClipboardFormat('PNG')


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
    for fmt in list(Format):
        if clipboard.IsClipboardFormatAvailable(fmt.value):
            clipboard.OpenClipboard()
            data = clipboard.GetClipboardData(fmt.value)
            clipboard.CloseClipboard()
            return data, fmt
    else:
        log_file.log(Tag.ERROR, 'Unknown copied data format')
        return current_data, current_format


def detect_local_copy():
    global current_data
    global current_format

    new_data, new_format = get_copied_data()
    if server_url and new_data != current_data:
        log_file.log(Tag.INFO, 'New data copied on local machine')
        current_data = new_data
        current_format = new_format
        file = BytesIO()
        file.write(current_data)
        file.seek(0)
        requests.post(server_url + '/clipboard', data=file, headers={'Data-Type': format_to_type[current_format]})


def detect_server_change():
    global current_data
    global current_format

    try:
        headers = requests.head(server_url + '/clipboard')
        if headers.ok and headers.headers['Data-Attached'] == 'True':
            data_request = requests.get(server_url + '/clipboard')
            log_file.log(Tag.INFO, 'New clipboard data has been received')
            clipboard.OpenClipboard()
            clipboard.EmptyClipboard()
            clipboard.SetClipboardData(type_to_format[data_request.headers['Data-Type']].value, data_request.content)
            clipboard.CloseClipboard()
            current_data, current_format = get_copied_data()
        elif not headers.ok:
            log_file.log(Tag.ERROR, 'Invalid response from server')
    except requests.exceptions.ConnectionError:
        log_file.log(Tag.ERROR, 'Lost connection to server')
        find_server()
        time.sleep(listener_delay)


def listener():
    while True:
        if server_url:
            detect_local_copy()
            detect_server_change()
        time.sleep(0.3)


if __name__ == '__main__':
    server_port = 5000
    finding_server_delay = 2
    listener_delay = 0.3
    log_file = Log('client_log.txt')

    server_url = ''
    ipaddr = gethostbyname(gethostname())
    base_ipaddr = '.'.join(ipaddr.split('.')[:-1])

    current_data, current_format = get_copied_data()

    format_to_type = {Format.TEXT: 'text', Format.IMAGE: 'image'}
    type_to_format = {v: k for k, v in format_to_type.items()}

    systray = SysTrayIcon('static/systray_icon.ico', 'Common Clipboard')
    systray.start()

    log_file.log(Tag.INFO, 'Starting search for server')

    finder_thread = Thread(target=find_server, daemon=True)
    finder_thread.start()

    listener_thread = Thread(target=listener, daemon=True)
    listener_thread.start()
