import serial
import asyncio
import time
#Serial setup
ser = serial.Serial('/dev/ttyACM0')



class Command:
    def __init__(self, timeline=[]):
        self.timeline = timeline
    def addCommand(self, timestamp, pinout, pulse):
        timeline.append((timestamp,pinout,pulse))
    def run(self, loop, device):
        for pinout, timestamp, pulse in self.timeline:
            loop.call_soon_threadsafe(loop.call_later, timestamp, self.execute, device, pinout, pulse)
    def execute(self, device, pinout, pulse):
        print("executing opcode " + pinout)
        if device is not None : 
            ser.write(device)
        if pulse:
            prefix = '0100'
        else:
            prefix = '0000'
        ser.write(bytes([int(prefix+pinout[0:4],2),int(pinout[4:],2)]))

test = Command([('000000000001',0, True)])

def learn_command():
    ser.write(b'\xFF\xFF')

def cancel_command():
    ser.write(b'\xFF\xFF')

def save_command(name):
    ser.write(b'\x00\x00')
    newcommand = Command()
    while True:
        rawtimestamp = ser.read(2)
        rawpinout = ser.read(2)
        if rawtimestamp == b'\xFF\xFF' and rawpinout == b'\xFF\xFF':
            break
        if newcommand.timeline[-1] is None:
            timestamp = 0
            pulse = False
        else:
            timestampbits = "{0:b}".format(int.from_bytes(rawtimestamp,'big'))
            timestampbits.zfill(16)
            mantissa = timestampbits[0]
            value = int(timestampbits[1:], 2)
            if mantissa == "0":
                value = value * 0.001
            if value < 0.1:
                pulse = True
            else:
                pulse = False
            timestamp = newcommand.timeline[-1][0] + value
        pinout = "{0:b}".format(int.from_bytes(rawpinout,'big'))
        newcommand.addCommand(timestamp, pinout, pulse)
        commandDict[name] = newcommand


commandDict = {
        "Test" : test,
        "Zero" : Command([('000000000000',0, False)])
}
