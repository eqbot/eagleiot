import serial
import asyncio
import time
#Serial setup
ser = serial.Serial('/dev/ttyUSB0')



class Command:
    def __init__(self, timeline=[]):
        self.timeline = timeline
    def addCommand(self, timestamp, pinout, pulse):
        timeline.append((timestamp,pinout,pulse))
    def run(self, loop):
        for i in self.timeline:
            device = i[1]
            value = self.timeline[i]
            loop.call_soon_threadsafe(loop.call_later, value[0], self.execute, device, value[1], value[2])
    def execute(self, device, pinout, pulse):
        print("executing opcode " + pinout)
        if device is not 1: 
            ser.write(device)
        if pulse:
            prefix = '0100'
        else:
            prefix = '0000'
        ser.write(bytes([int(prefix+pinout[0:4],2),int(pinout[4:],2)]))

test = Command([(0, '000000000001', True)])

def learn_command():
    ser.write(b'\xFF\xFF')

def cancel_command():
    ser.write(b'\xFF\xFF')

def save_command(name, devid):
    ser.write(b'\x00\x00')
    newcommand = Command()
    while True:
        rawtimestamp = ser.read(2)
        rawpinout = ser.read(2)
        pinout = "{0:b}".format(int.from_bytes(rawpinout,'big'))
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
                for i in range(0, 12):
                    if newcommand.timeline[-1][1][i] == pinout[i]:
                        pinout[i] = '0'
                    else:
                        pinout[i] = '1'
            else:
                pulse = False
            timestamp = newcommand.timeline[-1][0] + value
        newcommand.addCommand(timestamp, pinout, pulse)
        commandDict[(name,devid)] = newcommand


commandDict = {
        ("Test",1) : test,
        ("Zero",1) : Command([(0, '000000000000', False)]),
        ("TurnOnDevice",1) : Command([0,'00001111100',False])
}
