const server_url = args.shortcutParameter['server url']
const current_data = args.shortcutParameter['current data']
const new_data = args.shortcutParameter['new data']

if (new_data !== current_data) {
    let request = new Request(`http://${server_url}/clipboard`)
    request.method = 'post'
    request.headers = {'Content-Type': 'application/json'}
    request.body = JSON.stringify({'data': new_data})
    await request.load()
}

Script.complete()
