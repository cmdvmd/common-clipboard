import requests
import time
import win32clipboard as clipboard
from socket import gethostbyname, gethostname
from threading import Thread
from enum import Enum
from infi.systray import SysTrayIcon
from io import BytesIO
from plyer import notification


class Format(Enum):
    TEXT = clipboard.CF_UNICODETEXT
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


def get_copied_data():
    for fmt in list(Format):
        if clipboard.IsClipboardFormatAvailable(fmt.value):
            clipboard.OpenClipboard()
            data = clipboard.GetClipboardData(fmt.value)
            clipboard.CloseClipboard()
            return data, fmt
    else:
        try:
            return current_data, current_format
        except NameError:
            return '', Format.TEXT


def detect_local_copy():
    global current_data
    global current_format

    new_data, new_format = get_copied_data()
    if server_url and new_data != current_data:
        current_data = new_data
        current_format = new_format

        file = BytesIO()
        file.write(current_data.encode() if current_format == Format.TEXT else current_data)
        file.seek(0)
        requests.post(server_url + '/clipboard', data=file, headers={'Data-Type': format_to_type[current_format]})


def detect_server_change():
    global current_data
    global current_format

    try:
        headers = requests.head(server_url + '/clipboard')
        if headers.ok and headers.headers['Data-Attached'] == 'True':
            data_request = requests.get(server_url + '/clipboard')
            data_format = type_to_format[data_request.headers['Data-Type']]
            data = data_request.content.decode() if data_format == Format.TEXT else data_request.content

            clipboard.OpenClipboard()
            clipboard.EmptyClipboard()
            clipboard.SetClipboardData(data_format.value, data)
            clipboard.CloseClipboard()
            current_data, current_format = get_copied_data()
    except requests.exceptions.ConnectionError:
        notification.notify(
            title='Connection Error',
            message='Lost connection to Common Clipboard Server',
            timeout=5
        )
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

    server_url = ''
    ipaddr = gethostbyname(gethostname())
    base_ipaddr = '.'.join(ipaddr.split('.')[:-1])

    current_data, current_format = get_copied_data()

    format_to_type = {Format.TEXT: 'text', Format.IMAGE: 'image'}
    type_to_format = {v: k for k, v in format_to_type.items()}

    systray = SysTrayIcon('static/systray_icon.ico', 'Common Clipboard')
    systray.start()

    finder_thread = Thread(target=find_server, daemon=True)
    finder_thread.start()

    listener_thread = Thread(target=listener, daemon=True)
    listener_thread.start()
