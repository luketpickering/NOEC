# MicroPython, for RP2xx0 on Maker Pi Pico
from time import sleep
import asyncio
from machine import Pin, I2C
from neopixel import NeoPixel
import random

import mcp23017
from PicoADC16 import PicoADC16

i2c = I2C(1, scl=Pin(19), sda=Pin(18))
print(f"i2c scan results: {i2c.scan()}")
mcp = mcp23017.MCP23017(i2c, 32)
mcp[0].output(1)

adc = PicoADC16(cs_pins=[1,17])

neopin = Pin(16, Pin.OUT, value=0)
sleep(0.001)  # reset WS2812B
np = NeoPixel(neopin, 160, bpp=3, timing=(300,800,800,300))

cols = [ (32,32,32), (32,0,0), (0,32,0), (0,0,32), (0,32,32), (32,32,0) ]

async def rndmlights():
    while True:
        for i in range(160):
            np[i] = cols[random.randint(0,5)]
        np.write()
        await asyncio.sleep(0.25)

async def blinkled():
    out = False
    while True:
        out = not out
        mcp[0].output(out)
        await asyncio.sleep(0.25)

loop = asyncio.get_event_loop()

async def readallforever():
    while True:
        print(adc.read([0,1,2,3,4]))
        await asyncio.sleep(0.25)

tasks = []
tasks.append(loop.create_task(rndmlights()))
tasks.append(loop.create_task(blinkled()))
tasks.append(loop.create_task(readallforever()))

loop.run_forever()
