// Credit to Airwave by thura10

const name = args.shortcutParameter['name']
const ipaddr = args.shortcutParameter['ipaddr']
const server_port = args.shortcutParameter['port']
const timeout = args.shortcutParameter['timeout']

const base_ipaddr = ipaddr.split('.').slice(0, -1).join('.')

async function test_server_ip(index) {
    let tested_url = `${base_ipaddr}.${index}:${server_port}`

    let request = new Request(`http://${tested_url}/register`)
    request.method = 'post'
    request.headers = {'Content-Type': 'application/json'}
    request.body = JSON.stringify({'name': name})
    await request.load()

    Script.setShortcutOutput(tested_url)
    Script.complete()
}

for (let i = 1; i < 255; i++) {
    test_server_ip(i)
}

Timer.schedule(timeout, false, Script.complete)
