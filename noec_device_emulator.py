#! /usr/bin/env python3



import os, pty
import time, random

import json

from noec_utils import obj_to_msg
ADC_MAX = 1024

def openEmulator():
  # Open a new pseudo-terminal pair
  devicefd, clientfd = pty.openpty()
  client_tty = os.ttyname(clientfd)
  return devicefd,clientfd,client_tty

def startEmulator( devicefd,clientfd,client_tty):
  every_ms = 100.0
  do_update_prob = 100
  update_rate_ADC = 3

  num_vals = 4
  vals = [random.randint(0,ADC_MAX) for x in range(num_vals+1)]
  vals[4] = int((1300/6400) * ADC_MAX) #baseline in /radius

  vals_goal_adc = [random.randint(0,ADC_MAX) for x in range(num_vals+1)]

  num_states = 5
  states = [0 for x in range(num_states)]
  tick = 0
  hist = False
  noise = False

  while True:

    for i in range(num_vals):
      if random.randint(0,do_update_prob) == 0:
        vals_goal_adc[i] = random.randint(0,ADC_MAX)


      if vals[i] != vals_goal_adc[i]:
        delta = min(update_rate_ADC, abs(vals_goal_adc[i] - vals[i]))
        vals[i] += delta * (1 if vals_goal_adc[i] > vals[i] else -1)

    hist_random = random.randint(0,do_update_prob)
    noise_random = random.randint(0,do_update_prob)
    if hist_random == 0:
      hist = not hist

    if noise_random ==0:
      noise = not noise
        

    os.write(devicefd,str.encode('{{') +  obj_to_msg({"cmd": "UPDATE","hist":hist, "tick": tick, "states": states, "ADCs": vals, "ADCStates": [True, True, True, True], "noise":noise, "start_ml":False, "slow_load":False, "L_km":1300})+ str.encode('}}'))
    os.write(devicefd, str.encode('\n'))

       # print(f"{tick} -- Update: vals = {vals}")


    time.sleep(every_ms/1000.0)
    tick += 1

if __name__ == "__main__":
    devicefd,clientfd,client_tty = openEmulator()
    print("Client TTY name:", client_tty)
    input("Press Enter to start device emulator")
    
