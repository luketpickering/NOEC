# MicroPython, for RP2xx0 on Maker Pi Pico
from time import sleep
import asyncio
from machine import Pin, I2C, SPI
from neopixel import NeoPixel
import random

import mcp23017

i2c = I2C(1, scl=Pin(19), sda=Pin(18))
print(f"i2c results: {i2c.scan()}")
mcp = mcp23017.MCP23017(i2c, 32)
mcp[0].output(1)

spi_adc = SPI(0, baudrate=1_000_000, polarity=0, phase=0, sck=2, mosi=3, miso=4)
adc_a_cs = Pin(1, mode=Pin.OUT, value=1)
adc_b_cs = Pin(17, mode=Pin.OUT, value=1)

bufs = [bytearray(3), bytearray(3)]
bufs[0][0] = 0x01
bufs[0][1] = (0x01 << 7)

def readadc(chan):
    cspin = adc_b_cs if (chan >= 8) else adc_a_cs
    bchan = (chan % 8)

    bufs[0][1] = (0x01 << 7) | (bchan << 4)

    print(f"TX: 0b{bufs[0][0]:08b}, 0b{bufs[0][1]:08b}, 0b{bufs[0][2]:08b}")
    cspin(0)
    spi_adc.write_readinto(bufs[0],bufs[1])
    cspin(1)
    print(f"RX: 0b{bufs[1][0]:08b}, 0b{bufs[1][1]:08b}, 0b{bufs[1][2]:08b}")

    return int( ((bufs[1][1] & 0x03) << 8 ) | bufs[1][2])

def readall():
    return [readadc(i) for i in range(16)]

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

def readallforever():
    while True:
        print(readall())
        await asyncio.sleep(0.25)

tasks = []
tasks.append(loop.create_task(rndmlights()))
tasks.append(loop.create_task(blinkled()))
tasks.append(loop.create_task(readallforever()))

loop.run_forever()
