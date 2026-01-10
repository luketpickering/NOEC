from machine import ADC, Pin, Timer
from time import sleep

import sys

led = Pin(15, Pin.OUT)
tim = Timer()
def tick(timer):
    global led
    led.toggle()

tim.init(freq=2.5, mode=Timer.PERIODIC, callback=tick)

def ADC2V(adc):
    vread = adc * 3.3 / (65535)
    return vread

def ADC2Temp(adc):
    temp = 27 - (ADC2V(adc) - 0.706)/0.001721
    return temp

def dbgadcread():
    tempadc = machine.ADC(4)
    adc = tempadc.read_u16()
    print(f"temp measured: %s V = %s C" % (ADC2V(adc), ADC2Temp(adc)) )

    vsysadc = machine.ADC(Pin(29))
    adc = vsysadc.read_u16()
    print(f"VSYS measured: %s V " % (ADC2V(adc)*3) )

    adc2 = machine.ADC(Pin(28))
    adc = adc2.read_u16()
    print(f"ADC2 measured: %s V " % (ADC2V(adc)) )

    adc1 = machine.ADC(Pin(27))
    adc = adc1.read_u16()
    print(f"ADC1 measured: %s V " % (ADC2V(adc)) )

    adc0 = machine.ADC(Pin(26))
    adc = adc0.read_u16()
    print(f"ADC0 measured: %s V " % (ADC2V(adc)) )

ADCs = [ machine.ADC(Pin(p)) for p in [26, 27, 28] ]
def adcread():
    global ADCs
    return [adc.read_u16() for adc in ADCs]

def escape_msg(bytstr):
  obs = b''
  for c in bytstr:
    if c == 0xf1:
      obs += b'\xe0\xe1'
    elif c == 0xf2:
      obs += b'\xe0\xe2'
    elif c == 0xf3:
      obs += b'\xe0\xe3'
    elif c == 0xe0:
      obs += b'\xe0\xe0'
    else:
      obs += bytes([c])
  return obs

def vals2payload(vals):
    msg = b''
    for v in vals:
      msg += bytes([(v >> 8), v & 0xFF])
    return msg

def encode_msg(payload):
    msg = b'\xf1\x02\xf2' #update message
    msg += escape_msg(payload)
    msg += b'\xf3'
    return msg

while True:
    vals = adcread()
    #print(vals)
    payload = vals2payload(vals)
    #print("msg payload", ''.join("{:02X}".format(x) for x in payload))
    esc_payload = escape_msg(payload)
    #print("esc payload", ''.join("{:02X}".format(x) for x in esc_payload))
    msg = encode_msg(payload)
    #print("msg bytes  ", ''.join("{:02X}".format(x) for x in msg))
    sys.stdout.buffer.write(msg)
    sleep(1)