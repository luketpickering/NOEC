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
do_update_prob = 0
num_vals = 4
vals = [0 for x in range(num_vals+1)]
vals[4] = int((1300/6400) * 255)
num_states = 5
states = [0 for x in range(num_states)]
tick = 0

while True:
  rnint = random.randint(0,do_update_prob)
  if rnint == 0:

    key = random.randint(0,num_vals-1)
    delta = random.randint(-32,64) if vals[key] <= 127 else random.randint(-64,32)
    nval =  min(max(vals[key] + delta,0),255)
    vals[key] =nval

    os.write(devicefd, b'\xf1')
    os.write(devicefd, obj_to_msg({"cmd": "UPDATE", "tick": tick, "states": states, "ADCs": vals}))
    os.write(devicefd, b'\xf2')

    print(f"{tick} -- Update: values[{key}] = {vals[key]} ADC")

  else:
    print(f"{tick} -- No update")

  time.sleep(every_ms/1000.0)
  tick += 1
