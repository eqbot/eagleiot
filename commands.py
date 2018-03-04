import serial
import asyncio
#Serial setup
ser = serial.Serial('/dev/ttyACM0')

commandDict = {
        "Test": 0b10000000
        "Zero": 
}

class Command():
    def __init__(self,device, timeline=[]):
        self.device = device
        self.timeline = timeline
    def addCommand(timestamp, pinout):
        timeline.append((timestamp,pinout))
    async def exec():
        time = 0.0;
        for timestamp, pinout in timeline:
            await asyncio.sleep(timestamp-time)
            time += timestamp-time
            ser.write(device)
            ser.write(bytes([int('1000'+pinout[0:4],2),int(pinout[4:],2)])

zero = Command(1, [('000000000000',0)])
test = Command(1, [('000000000001',0)])
                    
commandDict = {
        "Test": test
        "Zero": zero
}


