#! /usr/bin/env python3

import asyncio
import serial
import json

from noec_utils import msg_to_obj

class NOECHost:
  def __init__(self, serial_device, baud=9600):
    self.ser = serial.Serial(serial_device, baud)
    self.previous = json.loads('{"cmd": "UPDATE", "tick": 0, "states": [0,0,0,0,0], "ADCs": [0,0,0,0], "ADCStates":[true,true,true,true], "noise": false, "hist":false, "start_ml":false, "slow_load":false, "L_km":1300, "ml_mode": "GD"}')

  def read_message(self):
    obj = self.ser.readline()[2:-3]
    print(obj)
    obj = obj.decode("utf-8")
    if obj != "" and obj is not None and obj[0] == "{" and obj[-1] == "}":
      self.previous = json.loads(str(obj))
      print(str(obj))
      return  json.loads(str(obj))
    return self.previous

  async def read(self):
    return await asyncio.get_event_loop().run_in_executor(None, self.read_message)

async def read_forever(host):
  while True:
    
    obj = await host.read()
    obj = obj.decode("utf-8")
    if obj != "" and obj is not None and obj[0] == "{" and obj[-1] == "}":
        obj = json.loads(str(obj))
        print("success")
    else:
      print("fail")

    

if __name__ == '__main__':
  import sys

  asyncio.run(read_forever(NOECHost(sys.argv[1])))
