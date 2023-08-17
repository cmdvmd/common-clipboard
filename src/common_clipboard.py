import requests
import time
import win32clipboard as clipboard
import sys
import pickle
from socket import gethostbyname, gethostname
from threading import Thread
from multiprocessing import Process
from multiprocessing.managers import BaseManager
from enum import Enum
from pystray import Icon, Menu, MenuItem
from PIL import Image
from io import BytesIO
from server import run_server
from device_list import DeviceList
from port_editor import PortEditor


class Format(Enum):
    TEXT = clipboard.CF_UNICODETEXT
    IMAGE = clipboard.RegisterClipboardFormat('PNG')


def test_server_ip(index):
    global server_url

    try:
        if not server_url:
            tested_url = f'http://{base_ipaddr}.{index}:{port}'

            response = requests.post(tested_url + '/register', json={'name': gethostname()})
            assert response.ok

            server_url = tested_url
    except (requests.exceptions.ConnectionError, AssertionError):
        return


def find_server():
    global server_url

    systray.title = 'Common Clipboard: Not Connected'
    server_url = ''
    while run_app and not server_url:
        for i in range(1, 255):
            test_url_thread = Thread(target=test_server_ip, args=(i,), daemon=True)
            test_url_thread.start()
        time.sleep(finding_server_delay)
    systray.title = 'Common Clipboard: Connected'


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
        find_server()


def listener():
    while run_app:
        if server_url:
            detect_local_copy()
            detect_server_change()
        systray.update_menu()
        time.sleep(listener_delay)


def start_server(toggle_variable=False):
    global running_server
    global server_process

    if toggle_variable:
        running_server = not running_server

    if running_server:
        server_process = Process(target=run_server, args=(port, connected_devices,))
        server_process.start()
    else:
        server_process.terminate()
        server_process = None


def close():
    global run_app

    run_app = False
    if server_process is not None:
        server_process.terminate()
    with open(preferences_file, 'wb') as save_file:
        pickle.dump([port, running_server], save_file)
    systray.stop()
    sys.exit(0)


def edit_port():
    global port

    port_dialog = PortEditor(port)
    new_port = port_dialog.port_number.get()
    if port_dialog.applied and new_port != port:
        port = new_port
        if running_server and server_process is not None:
            server_process.terminate()
            start_server()


def get_menu_items():
    menu_items = (
        MenuItem(f'Port: {port}', Menu(MenuItem('Edit', lambda _: edit_port()))),
        MenuItem('Run Server', lambda: start_server(True), checked=lambda _: running_server),
        MenuItem('View Connected Devices', Menu(lambda: (
            MenuItem(f"{name} ({ip})", None) for ip, name in connected_devices.get_devices()
        ))) if running_server else None,
        MenuItem('Quit', close),
    )
    return (item for item in menu_items if item is not None)


if __name__ == '__main__':
    finding_server_delay = 1
    listener_delay = 0.3

    server_url = ''
    ipaddr = gethostbyname(gethostname())
    base_ipaddr = '.'.join(ipaddr.split('.')[:-1])

    BaseManager.register('DeviceList', DeviceList)
    manager = BaseManager()
    manager.start()
    connected_devices = manager.DeviceList()

    server_process: Process = None

    preferences_file = 'preferences.pickle'
    try:
        with open(preferences_file, 'rb') as preferences:
            port, running_server = pickle.load(preferences)
    except FileNotFoundError:
        port = 5000
        running_server = False

    if running_server:
        start_server()

    current_data, current_format = get_copied_data()

    format_to_type = {Format.TEXT: 'text', Format.IMAGE: 'image'}
    type_to_format = {v: k for k, v in format_to_type.items()}

    icon = Image.open('icon.ico')
    systray = Icon('Common Clipboard', icon=icon, title='Common Clipboard', menu=Menu(get_menu_items))
    systray.run_detached()

    run_app = True

    find_server()
    listener()
