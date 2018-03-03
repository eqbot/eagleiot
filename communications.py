import websocket
import asyncio
import serial
import ssl
import json
from commands import commandDict
from threading import Thread
from uuid import getnode as get_mac

#websocket setup
HOSTNAME = 'wss://eagleiot.net'
websocket.enableTrace(True)

#Serial setup
#ser = serial.Serial('/dev/ttyUSB0')


def start_loop(loop):
    asyncio.set_event_loop(loop)
    loop.run_forever()

commandloop = asyncio.new_event_loop()
t = Thread(target=start_loop, args=(commandloop,))
t.start()

learning = False
learncmdName = ""

def reconnect(ws):
    if ws is not None:
        ws.close()
    ws = websocket.WebSocketApp(HOSTNAME, on_message=doCommand, on_close=on_close, on_error=on_error)

def doCommand(ws, msg):
    jsonblob = json.loads(msg)
    command = jsonblob['command']
    if learning:
        if command == "cancel":
            commands.cancel_command()
            learning = False
        if command == "save":
            commands.save_command(learncmdName)
            learning = False
    if command == "address":
        ws.send(json.dumps({"command":"address", "address":str(hex(get_mac()))}))
        return
    if command == "learn":
        commands.learn_command()
        learning = True
        learncmdName = jsonblob['name']
    devname = json.loads(msg)['id']
    command = commandDict[command]
    if command is not None:
        command.run(commandloop, devname)

def on_close(ws):
    print("connection end")
    commandloop.stop()

def runSocket():
    reconnect(ws)
    ws.run_forever()

def on_open(ws):
    print("opening")
    def run(*args):
        pass

def on_error(ws, error):
    print(error)

ws = websocket.WebSocketApp(HOSTNAME, on_message=doCommand, on_close=on_close, on_error=on_error, header=['Sec-WebSocket-Protocol:test'])
ws.on_open = on_open
print("I initialized ws")
#runSocket()
ws.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE, "check_hostname": False})
print("run_forever ended")
