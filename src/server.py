from flask import Flask, request, make_response, send_file
from io import BytesIO
from device_list import DeviceList

app = Flask(__name__)


@app.route('/register', methods=['POST'])
def register():
    device_info = request.get_json()
    try:
        connected_devices.add_device(request.remote_addr, device_info['name'])
        return '', 204
    except KeyError:
        return 'Provided device information is invalid', 400


@app.route('/clipboard', methods=['GET', 'HEAD'])
def send_clipboard():
    try:
        connected_devices.update_activity(request.remote_addr)
        if not connected_devices.get_received(request.remote_addr):
            file = BytesIO()
            file.write(clipboard)
            file.seek(0)
            response = make_response(send_file(file, mimetype=data_type))
            response.headers['Data-Attached'] = 'True'
            response.headers['Data-Type'] = data_type
            if request.method != 'HEAD':
                connected_devices.set_received(request.remote_addr, True)
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
        connected_devices.update_activity(request.remote_addr)
        assert 'Data-Type' in request.headers, 'Missing data type header'
        clipboard = request.get_data()
        data_type = request.headers['Data-Type']
        for ip, _ in connected_devices.get_devices():
            connected_devices.set_received(ip, ip == request.remote_addr)
        return '', 204
    except KeyError:
        return unregistered_error
    except AssertionError as e:
        return str(e), 400


def run_server(port, device_list):
    global connected_devices

    connected_devices = device_list
    app.run(host='0.0.0.0', port=port)


unregistered_error = 'The requesting device is not registered to the server', 401

clipboard = b''
data_type = 'text'
connected_devices = DeviceList()
