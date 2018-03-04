import websocket
import asyncio
import serial
from commands import commandDict, execCommand

#websocket setup
HOSTNAME = 'ws://eagleiot.net'

#Serial setup
ser = serial.Serial('/dev/ttyACM0')

def reconnect(ws):
    if ws is not None:
        ws.close()
    ws = websocket.WebSocketApp(HOSTNAME, on_message=doCommand, on_close=on_close, on_error=on_error)

def doCommand(ws, msg):
    data = msg.split()
    devname = data[0]
    command = commandDict.get(' '.join(data[1:]))
    command.exec()

def on_close(ws):
    print("connection end")
def runSocket():
    reconnect(ws)
    ws.run_forever()

def on_open(ws):
    ws.send("Hello, I'm a new device!")

def on_error(ws, error):
    print(error)

ws = websocket.WebSocketApp(HOSTNAME, on_message=doCommand, on_close=on_close, on_error=on_error)

runSocket()
