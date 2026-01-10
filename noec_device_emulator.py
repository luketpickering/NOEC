#! /usr/bin/env python3

import os, pty
import time, random

import json

from noec_utils import obj_to_msg

# Open a new pseudo-terminal pair
devicefd, clientfd = pty.openpty()

client_tty = os.ttyname(clientfd)

print("Client TTY name:", client_tty)

input("Press Enter to start device emulator")

every_ms = 50.0
do_update_prob = 1
num_vals = 20
vals = [0 for x in range(num_vals)]
tick = 0

while True:
  rnint = random.randint(0,do_update_prob)
  if (rnint == 0) or (tick % 20) == 0:

    if (rnint == 0):
      key = random.randint(0,num_vals-1)
      delta = random.randint(-127,385) if vals[key] <= 2047 else random.randint(-385,127)
      nval =  min(max(vals[key] + delta,0),4095)
      vals[key] =nval

    os.write(devicefd, b'\xf1')
    os.write(devicefd, obj_to_msg({"cmd": "UPDATE", "tick": tick, "vals": vals}))
    os.write(devicefd, b'\xf2')

    if (rnint == 0):
      print(f"{tick} -- Update: values[{key}] = {vals[key]} ADC")
    else:
      print(f"{tick} -- Heartbeat")

  else:
    print(f"{tick} -- No update")

  time.sleep(every_ms/1000.0)
  tick += 1
