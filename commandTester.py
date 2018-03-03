import commands
import asyncio
import functools
from threading import Thread

test = commands.Command([('000000000010',0)])

def start_loop(loop):
    asyncio.set_event_loop(loop)
    loop.run_forever()

commandloop = asyncio.new_event_loop()
t = Thread(target=start_loop, args=(commandloop,))
t.start()


#test.run(commandloop, None)
ser = commands.ser
ser.write(b'\xFF')
print(ser.readline())
ser.write(b'\xF0')
