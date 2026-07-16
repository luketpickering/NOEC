from time import sleep
import asyncio
from machine import Pin, I2C, SPI, ADC
from neopixel import NeoPixel
import random
import mcp23017
from time import sleep
from noec_utils import *
import sys

i2c = I2C(1, scl=Pin(19), sda=Pin(18))
#print(f"i2c results: {i2c.scan()}")
mcp = mcp23017.MCP23017(i2c, 32)
mcp[0].output(1)


hist_pin = Pin(12, Pin.IN)
noise_pin = Pin(13, Pin.IN)
ml_pin = Pin(14, Pin.IN)
slow_load_pin = Pin(15, Pin.IN)
distance_pin = ADC(Pin(26))

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
    
    #print(f"TX: 0b{bufs[0][0]:08b}, 0b{bufs[0][1]:08b}, 0b{bufs[0][2]:08b}")
    cspin(0)
    spi_adc.write_readinto(bufs[0],bufs[1])
    cspin(1)
    #print(f"RX: 0b{bufs[1][0]:08b}, 0b{bufs[1][1]:08b}, 0b{bufs[1][2]:08b}")

    return int( ((bufs[1][1] & 0x03) << 8 ) | bufs[1][2])

def readfour():
    return [readadc(i) for i in range(12,16)]
    
tick = 0
while True:
    vals = readfour()
    num_states = 5
    states = [0 for x in range(num_states)]
    #print(distance_pin.read_u16())
    print(obj_to_msg({"cmd": "UPDATE", "tick": tick, "states": states, "ADCs": vals, "hist": bool(hist_pin.value()), "noise":bool(noise_pin.value()), "start_ml":bool(ml_pin.value()), "slow_load":bool(slow_load_pin.value()), "L_km": distance_pin.read_u16() >> 6}))
    tick +=1
    sleep(0.1)
    
