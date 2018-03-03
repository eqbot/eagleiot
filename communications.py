import websockets
import asyncio
from bluepy.btle import UUID, Peripheral, Scanner, DefaultDelegate, BTLEException
from commands import commandDict

#websocket setup
HOSTNAME = 'ws://eagleiot.net'

ws = websockets.client.connect(HOSTNAME)

#BTLE setup
temp_uuid = UUID(0x2221)

class ScanDelegate(DefaultDelegate):
    def __init__(self):
        DefaultDelegate.__init__(self)
    def handleDiscovery(self, dev, isNewDev, isNewData):
        if isNewDev:
            print("Discovered device", dev.addr)
        elif isNewData:
            print("Recieved new data from", dev.addr)

scanner = Scanner().withDelegate(ScanDelegate())
devices = scanner.scan(10.0)
peripherals = {}
for device in devices:
    print(device.getValueText(9))
    try:
        peripherals[device.getValueText(9)] = Peripheral(device)
    except BTLEException:
        continue

def reconnect():
    ws = websockets.client.connect(HOSTNAME)

def doCommand(msg):
    data = msg.split()
    devname = data[0]
    command = data[1]
    args = data[2:]

async def runloop():
    while True:
        try:
            msg = await asyncio.wait_for(ws.recv(), timeout = 60)
        except asyncio.TimeoutError:
            try:
                pong = await ws.ping()
                await asyncio.wait_for(pong, timeout = 60)
            except asyncio.TimeoutError:
                reconnect()
        else:
            doCommand(msg)


asyncio.get_event_loop().run_until_complete(runloop())
