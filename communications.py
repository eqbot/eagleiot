import websocket
import asyncio
import serial
import ssl
import json
import sys, select
import os
import commands
from commands import commandDict
from threading import Thread
from uuid import getnode as get_mac

learning = False
learncmdName = ""
learndevice = None

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


def reconnect(ws):
    if ws is not None:
        ws.close()
    ws = websocket.WebSocketApp(HOSTNAME, on_message=doCommand, on_close=on_close, on_error=on_error)

def doCommand(ws, msg):
    global learning, learncmdName, learndevice
    jsonblob = json.loads(msg)
    command = jsonblob['command']
    if learning:
        if command == "cancel":
            commands.cancel_command()
            learning = False
        if command == "save":
            commands.save_command(learncmdName)
            learning = False
    elif command == "address":
        ws.send(json.dumps({"command":"address", "address":str(hex(get_mac()))}))
        return
    elif command == "learn":
        commands.learn_command()
        learning = True
        learncmdName = jsonblob['name']
        learndevice = jsonblob['id']
    elif command == "ListenForNewDevice":
        name = jsonblob['id']
        if(commands.tryFindDevice()):
           ws.send(json.dumps({"command":"FoundNewDevice","address":str(hex(get_mac())),"name":name}))
        else:
            print("no device here")
    elif command == "EstablishOwnership":
        mac = jsonblob['mac']
        newid = jsonblob['id']
        if mac == str(hex(get_mac())):
            commands.finishPair(newid)
    else:
        devname = int(json.loads(msg)['id'])
        command = commandDict[(command,devname)]
        if command is not None:
            command.run(commandloop)

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
os._exit(0)
