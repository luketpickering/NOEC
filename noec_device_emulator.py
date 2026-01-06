#! /usr/bin/env python3

import os, pty
import time, random

import vals_pb2

# Open a new pseudo-terminal pair
devicefd, clientfd = pty.openpty()

client_tty = os.ttyname(clientfd)

print("Client TTY name:", client_tty)

input("Press Enter to start device emulator")

every_ms = 50
do_update_prob = 2
num_vals = 4
tick = 0

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

msgcmd = vals_pb2.Command()
msgupbody = vals_pb2.UpdateBody()

while True:

  msgcmd.cmd = vals_pb2.Command.command.UPDATE

  rnint = random.randint(0,do_update_prob)
  if (rnint == 0) or (tick % 20) == 0:

    if (rnint == 0):
      key = random.randint(0,num_vals)
      delta = random.randint(-127,385) if msgupbody.values[key] <= 2047 else random.randint(-385,127)

      msgupbody.values[key] = min(max(msgupbody.values[key] + delta,0),4095)

    print(f"{tick} -- message (unescaped) payload: %s" % ''.join(format(x, '02x') for x in msgcmd.SerializeToString() + msgupbody.SerializeToString()))

    payload = b'\xf1' + escape_msg(msgcmd.SerializeToString()) + b'\xf2' + escape_msg(msgupbody.SerializeToString()) + b'\xf3'
    print(f"{tick} -- message (escaped) payload: %s" % ''.join(format(x, '02x') for x in payload))

    os.write(devicefd, payload)

    if (rnint == 0):
      print(f"{tick} -- Update: values[{key}] = {msgupbody.values[key]} ADC")
    else:
      print(f"{tick} -- Heartbeat")

  else:
    print(f"{tick} -- No update")

  time.sleep(every_ms/1000.0)
  tick += 1
