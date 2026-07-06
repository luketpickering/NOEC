#!/usr/bin/env python3

import json
import yaml
import asyncio
import sys

from websockets.asyncio.server import serve

from noec_host import NOECHost

from nufast import Probability_Matter_LBL

from math import pow, sin, pi

import numpy as np
import random

class InputProcessor:
  def __init__(self, cfg):
    self.cfg = cfg

    self.param_maps = []
    self.param_idx = {}
    

    for i, pdef in enumerate(self.cfg["noec"]["controls"]["parameters"]):
      min = pdef["range"][0]
      max = pdef["range"][1]
      adcmx = float(pdef["ADCMx"])

      self.param_idx[pdef["name"]] = i

      #this nightmare avoids all the functions keeping a reference to the
      #  variable in the loop and so all describing the same map, that of the
      #  last loop element
      def mapper(min, max, adcmx):
        return lambda x: min + (max-min)*(float(x)/adcmx)

      self.param_maps.append(mapper(min, max, adcmx))

      true_vals = [random.randint(0,255) for i in range(4)]
      true_vals_mapped = []
    for i, v in enumerate(true_vals):
      if i < len(self.param_maps):
        true_vals_mapped.append(self.param_maps[i](v))
    print(true_vals_mapped)
    self.true_Es, self.true_osc_probs, self.true_bosc_probs = self.calc_probs_hist(true_vals_mapped,1300, 30)
    
  def calc_probs(self, vals, L):

    Es = np.logspace(-0.3,0.8,100) #GeV
    rho = 3 # g/cc
    Ye = 0.5
    N_Newton = 0
    s12sq = 0.31
    # s13sq = pow(sin(vals[self.param_idx["Th13"]]*pi/180.0),2)
    s13sq = pow(sin(8.8*pi/180.0),2)
    s23sq = pow(sin(vals[self.param_idx["Th23"]]*pi/180.0),2)
    delta = vals[self.param_idx["dcp"]] * pi
    Dmsq21 = 7.5e-5 # eV^2
    Dmsq31 = vals[self.param_idx["Dm32"]] * 1e-3 # eV^2

    osc_probs = [ Probability_Matter_LBL(s12sq, s13sq, s23sq,
                                      delta, Dmsq21, Dmsq31,
                                      L, E, rho, Ye, N_Newton) for E in Es ]
    bosc_probs = [ Probability_Matter_LBL(s12sq, s13sq, s23sq,
                                      delta, Dmsq21, Dmsq31,
                                      L, -E, rho, Ye, N_Newton) for E in Es ]

    return Es, osc_probs, bosc_probs
  
  def calc_probs_hist(self, vals, L, num_bins):
    Es = np.logspace(-0.3,0.8,num_bins) #GeV
    print("Es:", Es) 
    rho = 3 # g/cc
    Ye = 0.5
    N_Newton = 0
    s12sq = 0.31
    # s13sq = pow(sin(vals[self.param_idx["Th13"]]*pi/180.0),2)
    s13sq = pow(sin(8.8*pi/180.0),2)
    s23sq = pow(sin(vals[self.param_idx["Th23"]]*pi/180.0),2)
    delta = vals[self.param_idx["dcp"]] * pi
    Dmsq21 = 7.5e-5 # eV^2
    Dmsq31 = vals[self.param_idx["Dm32"]] * 1e-3 # eV^2

    osc_probs = [ Probability_Matter_LBL(s12sq, s13sq, s23sq,
                                      delta, Dmsq21, Dmsq31,
                                      L, E, rho, Ye, N_Newton) for E in Es ]
    bosc_probs = [ Probability_Matter_LBL(s12sq, s13sq, s23sq,
                                      delta, Dmsq21, Dmsq31,
                                      L, -E, rho, Ye, N_Newton) for E in Es ]

    return Es, osc_probs, bosc_probs

  def calc_state_probs(self, tick, vals, L_max):

    nticks = 100
    L = L_max * float(tick % nticks)/float(nticks) # km
    E = 2.3 #GeV
    rho = 3 # g/cc
    Ye = 0.5
    N_Newton = 0
    s12sq = 0.31
    # s13sq = pow(sin(vals[self.param_idx["Th13"]]*pi/180.0),2)
    s13sq = pow(sin(8.8*pi/180.0),2)
    s23sq = pow(sin(vals[self.param_idx["Th23"]]*pi/180.0),2)
    delta = vals[self.param_idx["dcp"]] * pi
    Dmsq21 = 7.5e-5 # eV^2
    Dmsq31 = vals[self.param_idx["Dm32"]] * 1e-3 # eV^2

    probm = Probability_Matter_LBL(s12sq, s13sq, s23sq,
                                      delta, Dmsq21, Dmsq31,
                                      L, E, rho, Ye, N_Newton)

    probbar = Probability_Matter_LBL(s12sq, s13sq, s23sq,
                                      delta, Dmsq21, Dmsq31,
                                      L, -E, rho, Ye, N_Newton)

    return { "prob": [ [probm[0][0],probm[0][1],probm[0][2]],
                       [probm[1][0],probm[1][1],probm[1][2]],
                       [probm[2][0],probm[2][1],probm[2][2]] ],
             "probbar": [ [probbar[0][0],probbar[0][1],probbar[0][2]],
                          [probbar[1][0],probbar[1][1],probbar[1][2]],
                          [probbar[2][0],probbar[2][1],probbar[2][2]] ],
             "L": L }

  def calculate_likelihood(self, predicted,actual):
    return np.sum(np.power(predicted -actual ,2)/actual)

  def calc_lh_disp(self, predicted,actual):
    return round(100/np.exp(self.calculate_likelihood(predicted,actual)/2),0)

  def process(self, data):
    data["vals"] = []
    print(data["ADCs"])
    for i, v in enumerate(data["ADCs"]):
      if i < len(self.param_maps):
        data["vals"].append(self.param_maps[i](v))
    #print(data["vals"])
    data["L_km"] = 1300

    Es, osc_probs, bosc_probs = self.calc_probs(data["vals"], data["L_km"])
    data["osc_probs"] = {}
    data["true_osc_probs"] = {}
    data["osc_probs"]["numu"] = [ [Es[i], osc_probs[i][1][1], bosc_probs[i][1][1]] for i in range(len(osc_probs))]
    data["osc_probs"]["nue"] = [ [Es[i], osc_probs[i][1][0], bosc_probs[i][1][0]] for i in range(len(osc_probs))]
    data["true_osc_probs"]["nue"]= [[self.true_Es[i], self.true_osc_probs[i][1][0], self.true_bosc_probs[i][1][0]] for i in range(len(self.true_osc_probs))]
    data["trans_prob_max"] = self.calc_state_probs(int(data["tick"]), data["vals"], data["L_km"])
    data["osc_probs"]["likelihood"] = self.calc_lh_disp(np.array(data["osc_probs"]["nue"][1]),np.array(data["true_osc_probs"]["nue"][1]))
    print(1/np.exp(self.calculate_likelihood(np.array(data["osc_probs"]["nue"][1]),np.array(data["true_osc_probs"]["nue"][1]))/2))
    return data

def float_range(start, stop, step):
    while start < stop:
        yield start
        start += step
  
async def forward_to_ws(serial_device, baud, websocket):
  host = NOECHost(serial_device, baud)
  with open("ui_config.yaml", 'r') as yaml_in:
    uicfg = yaml.safe_load(yaml_in)

  ip = InputProcessor(uicfg)
  await websocket.send(json.dumps({"cmd": "ui_start", "cfg": uicfg}))
  while True:
    data_from_device = await host.read()
    data_to_ui = ip.process(data_from_device)
    await websocket.send(json.dumps(data_to_ui))

async def NOECWSServer(serial_device, baud=9600, ws_port=5678):
  async with serve(lambda ws: forward_to_ws(serial_device, baud, ws), "localhost", ws_port) as server:
    await server.serve_forever()

if __name__ == "__main__":
  asyncio.run(NOECWSServer(sys.argv[1]))
