import time
import webbrowser
from infi.systray import SysTrayIcon
from flask import Flask, request, render_template, make_response, send_file
from log import Log, Tag
from threading import Thread
from io import BytesIO

app = Flask(__name__)


@app.route('/', methods=['GET'])
def show_connected():
    if request.remote_addr == '127.0.0.1' or request.remote_addr in connected_devices:
        for ip, device in list(connected_devices.items()):
            if time.time() - device['last active'] >= 5:
                del connected_devices[ip]
                log_file.log(Tag.INFO, f"Unregistered {device['name']}")
        return render_template('index.html', device_list=connected_devices), 200
    else:
        return render_template('restricted.html'), 401


@app.route('/register', methods=['POST'])
def register():
    device_info = request.get_json()
    try:
        name = device_info['name']
        connected_devices.update({request.remote_addr: {
            'name': name,
            'last active': time.time(),
            'received': False
        }})
        log_file.log(Tag.INFO, f"Registered {name} ({request.remote_addr})")
        return '', 204
    except KeyError:
        return 'Provided device information is invalid', 400


@app.route('/clipboard', methods=['GET'])
def send_clipboard():
    try:
        connected_devices[request.remote_addr]['last active'] = time.time()
        if not connected_devices[request.remote_addr]['received']:
            file = BytesIO()
            file.write(clipboard)
            file.seek(0)
            response = make_response(send_file(file, mimetype=data_type))
            response.headers['Data-Attached'] = 'True'
            response.headers['Data-Type'] = data_type
            if request.method != 'HEAD':
                connected_devices[request.remote_addr]['received'] = True
        else:
            response = make_response()
            response.headers['Data-Attached'] = 'False'
        response.status_code = 200
        return response
    except KeyError:
        return unregistered_error


@app.route('/clipboard', methods=['POST'])
def update_clipboard():
    global clipboard
    global data_type

    try:
        connected_devices[request.remote_addr]['last active'] = time.time()
        assert 'Data-Type' in request.headers, 'Missing data type header'
        clipboard = request.get_data()
        data_type = request.headers['Data-Type']
        log_file.log(Tag.INFO,
                     f"Received new clipboard data from {connected_devices[request.remote_addr]['name']} ({request.remote_addr})")
        for ip in connected_devices:
            connected_devices[ip]['received'] = False
        return '', 204
    except KeyError:
        return unregistered_error
    except AssertionError as e:
        return str(e), 400


def close_server():
    log_file.log(Tag.INFO, 'Server closed')


if __name__ == '__main__':
    port = 5000
    unregistered_error = 'The requesting device is not registered to the server', 401

    clipboard = b''
    data_type = 'text'

    connected_devices = {}
    log_file = Log('server_log.txt')

    menu_options = (('View Connected Devices', None, lambda _: webbrowser.open(f'http://localhost:{port}')),)
    systray = SysTrayIcon('static/server_icon.ico', 'Common Clipboard Server', menu_options,
                          on_quit=lambda _: close_server())
    systray.start()

    log_file.log(Tag.INFO, 'Server started')
    server_thread = Thread(target=app.run, kwargs={'host': '0.0.0.0', 'port': port}, daemon=True)
    server_thread.start()
