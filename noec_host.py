#! /usr/bin/env python3

import asyncio
import serial
import json

from noec_utils import msg_to_obj

class NOECHost:
  def __init__(self, serial_device, baud=9600):
    self.ser = serial.Serial(serial_device, baud)

  def read_message(self):
    self.ser.read_until(b'\xf1') #message magic byte
    return msg_to_obj(self.ser.read_until(b'\xf2')[:-1])

  async def read(self):
    return await asyncio.get_event_loop().run_in_executor(None, self.read_message)

async def read_forever(host):
  while True:
    obj = await host.read()
    print(obj)

if __name__ == '__main__':
  import sys

  asyncio.run(read_forever(NOECHost(sys.argv[1])))
