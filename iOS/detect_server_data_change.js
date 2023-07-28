const server_url = args.shortcutParameter['server url']
const current_data = args.shortcutParameter['new data']

let request = new Request(`http://${server_url}/clipboard`)
request.method = 'get'

let copied_data = await request.loadJSON()
copied_data = copied_data['data']
if (copied_data !== current_data) Script.setShortcutOutput(copied_data)

Script.complete()
