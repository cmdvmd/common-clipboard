"""
Main file for application
"""

import requests
import time
import win32clipboard as clipboard
import sys
import os
import pickle
from socket import gethostbyname, gethostname
from threading import Thread
from multiprocessing import freeze_support, Value, Process
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


def register(index):
    global server_url

    server_url = f'http://{base_ipaddr}.{index}:{port}'
    requests.post(server_url + '/register', json={'name': gethostname()})


def test_server_ip(index):
    global server_url
    global running_server

    try:
        tested_url = f'http://{base_ipaddr}.{index}:{port}'
        response = requests.get(tested_url + '/timestamp', timeout=5)
        if response.ok and float(response.text) < server_timestamp.value:
            register(index)
            running_server = False
            server_process.terminate()
            systray.title = f'{app_name}: Connected'
    except (requests.exceptions.ConnectionError, AssertionError):
        return


def find_server():
    global running_server

    start_server()
    register(device_index)
    systray.title = f'{app_name}: Server Running'

    for i in range(1, 255):
        if i != device_index:
            test_url_thread = Thread(target=test_server_ip, args=(i,), daemon=True)
            test_url_thread.start()


def get_copied_data():
    try:
        for fmt in list(Format):
            if clipboard.IsClipboardFormatAvailable(fmt.value):
                clipboard.OpenClipboard()
                data = clipboard.GetClipboardData(fmt.value)
                clipboard.CloseClipboard()
                return data, fmt
        else:
            raise BaseException
    except BaseException:
        try:
            return current_data, current_format
        except NameError:
            return '', Format.TEXT


def detect_local_copy():
    global current_data
    global current_format

    new_data, new_format = get_copied_data()
    if new_data != current_data:
        current_data = new_data
        current_format = new_format

        file = BytesIO()
        file.write(current_data.encode() if current_format == Format.TEXT else current_data)
        file.seek(0)
        requests.post(server_url + '/clipboard', data=file, headers={'Data-Type': format_to_type[current_format]})


def detect_server_change():
    global current_data
    global current_format

    headers = requests.head(server_url + '/clipboard', timeout=2)
    if headers.ok and headers.headers['Data-Attached'] == 'True':
        data_request = requests.get(server_url + '/clipboard')
        data_format = type_to_format[data_request.headers['Data-Type']]
        data = data_request.content.decode() if data_format == Format.TEXT else data_request.content

        clipboard.OpenClipboard()
        clipboard.EmptyClipboard()
        clipboard.SetClipboardData(data_format.value, data)
        clipboard.CloseClipboard()
        current_data, current_format = get_copied_data()


def mainloop():
    find_server()
    while run_app:
        try:
            detect_local_copy()
            detect_server_change()
        except requests.exceptions.ConnectionError:
            systray.title = f'{app_name}: Not Connected'
            if run_app:
                find_server()
        except TimeoutError:
            continue
        finally:
            systray.update_menu()
            time.sleep(listener_delay)


def start_server():
    global running_server
    global server_process

    if server_process is not None:
        server_process.terminate()

    connected_devices.clear()
    running_server = True
    server_process = Process(target=run_server, args=(port, connected_devices, server_timestamp,))
    server_process.start()


def close():
    global run_app

    run_app = False
    if server_process is not None:
        server_process.terminate()

    with open(preferences_file, 'wb') as save_file:
        pickle.dump(port, save_file)

    systray.stop()
    sys.exit(0)


def edit_port():
    global port

    port_dialog = PortEditor(port)
    new_port = port_dialog.port_number.get()
    if port_dialog.applied and new_port != port:
        port = new_port
        find_server()


def get_menu_items():
    menu_items = (
        MenuItem(f'Port: {port}', Menu(MenuItem('Edit', lambda _: edit_port()))),
        MenuItem('View Connected Devices', Menu(lambda: (
            MenuItem(f"{name} ({ip})", None) for ip, name in connected_devices.get_devices()
        ))) if running_server else None,
        MenuItem('Quit', close),
    )
    return (item for item in menu_items if item is not None)


if __name__ == '__main__':
    freeze_support()

    app_name = 'Common Clipboard'
    listener_delay = 0.3

    server_url = ''
    ipaddr = gethostbyname(gethostname())
    split_ipaddr = ipaddr.split('.')
    base_ipaddr = '.'.join(split_ipaddr[:-1])
    device_index = int(split_ipaddr[-1])

    BaseManager.register('DeviceList', DeviceList)
    manager = BaseManager()
    manager.start()
    connected_devices = manager.DeviceList()
    server_timestamp = Value('d', 0)

    running_server = False
    server_process: Process = None

    try:
        data_dir = os.path.join(os.getenv('LOCALAPPDATA'), app_name)
    except TypeError:
        data_dir = os.getcwd()

    if not os.path.exists(data_dir):
        os.makedirs(data_dir)

    preferences_file = os.path.join(data_dir, 'preferences.pickle')
    try:
        with open(preferences_file, 'rb') as preferences:
            port = pickle.load(preferences)
    except FileNotFoundError:
        port = 5000

    current_data, current_format = get_copied_data()

    format_to_type = {Format.TEXT: 'text', Format.IMAGE: 'image'}
    type_to_format = {v: k for k, v in format_to_type.items()}

    icon = Image.open('systray_icon.ico')
    systray = Icon(app_name, icon=icon, title=app_name, menu=Menu(get_menu_items))
    systray.run_detached()

    run_app = True
    mainloop()
