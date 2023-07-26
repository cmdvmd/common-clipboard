from flask import Flask, request, render_template
from log import Log, Tag

app = Flask(__name__)


@app.route('/', methods=['GET'])
def show_connected():
    return render_template('index.html', device_list=connected_devices), 200


@app.route('/register', methods=['POST'])
def register():
    device_info = request.get_json()
    try:
        connected_devices.append((device_info['name'], device_info['ipaddr']))
        log_file.log(Tag.INFO, f"Registered {device_info['name']}")
        return '', 204
    except KeyError:
        return 'Provided device information is invalid', 400


@app.route('/remove', methods=['POST'])
def remove():
    try:
        device_ip = request.get_json()['ipaddr']
        for device in connected_devices:
            if device[1] == device_ip:
                connected_devices.remove(device)
                log_file.log(Tag.INFO, f"Unregistered {device[0]}")
                return '', 204
        else:
            return 'Provided device information is invalid', 400
    except KeyError:
        return 'Missing device ipaddr parameter', 400


@app.route('/clipboard', methods=['GET'])
def get_clipboard():
    return {'data': clipboard}, 200


@app.route('/clipboard', methods=['POST'])
def update_clipboard():
    global clipboard

    received_data = request.get_json()
    try:
        clipboard = received_data['data']
        log_file.log(Tag.INFO, 'Received new clipboard data')
        return '', 204
    except KeyError:
        return 'Missing clipboard data parameter', 400


if __name__ == '__main__':
    newline = '\n\t'

    clipboard = ''
    connected_devices = []

    log_file = Log('server_log.txt')
    log_file.log(Tag.INFO, 'Server started')

    app.run(host='0.0.0.0', port=5000)

    log_file.log(Tag.INFO, 'Server closed')
