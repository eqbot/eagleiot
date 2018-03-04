import serial
import asyncio
import time
import json
#Serial setup
ser = serial.Serial('/dev/ttyACM0')


configfile = 'commands.json'

class Command:
    def __init__(self, devid, timeline=[]):
        self.timeline = timeline
        self.devid = devid
    def addCommand(self, timestamp, pinout, pulse):
        timeline.append((timestamp,pinout,pulse))
    def run(self, loop):
        print(self.timeline)
        for timestamp, bitstring, pulse in self.timeline:
            loop.call_soon_threadsafe(loop.call_later, timestamp, self.execute, self.devid, bitstring, pulse)
    def execute(self, device, pinout, pulse):
        print("executing opcode " + pinout)
        ser.write(chr(device))
        if pulse:
            prefix = '0100'
        else:
            prefix = '0000'
        ser.write(bytes([int(prefix+pinout[0:4],2),int(pinout[4:],2)]))

class CommandEncoder(json.JSONEncoder):
    def default(self,obj):
        if isinstance(obj, Command):
            return {'__cmd__':True, 'devid': obj.devid, 'timeline': obj.timeline}
        return json.JSONEncoder.default(self, obj)

def as_command(dct):
    if '__cmd__' in dct:
        return Command(dct['devid'], dct['timeline'])
    return dct

def remap_key(mapping):
    return [{'key': i[0], 'value':i[1]} for i in mapping.items()]

def unmap_keys(mapping):
    dictmap = {}
    for diction in mapping:
        dictmap[(diction['key'][0],diction['key'][1])] = diction['value']
    return dictmap

def tryFindDevice():
    ser.write(b'\x00') #find on channel 0
    ser.write(b'\x00\x00')
    ser.timeout = 1
    try:
        ser.read(2)
    except:
        ser.write(b'\x00\x00\x00')
        return False
    return True

def finishPairing(devid):
    ser.write(b'\x00')
    ser.write(chr(devid))
    ser.write(b'\x00')

test = Command(1, [(0, '000000000001', True)])

def learn_command():
    ser.write(b'\xFF\xFF')

def cancel_command():
    ser.write(b'\xFF\xFF')

def save_command(name, devid):
    ser.write(b'\x00\x00')
    newcommand = Command(devid)
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
            if value < 0.5:
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
        fp = open(configfile, "w")
        json.dump(commandDict, fp)
        fp.close()


fp = open(configfile, "r")
commandDict = unmap_keys(json.load(fp, object_hook=as_command))
fp.close()

