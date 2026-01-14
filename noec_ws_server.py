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

  def calc_probs(self, vals):

    L = 1300 # km
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

    return Es, osc_probs, bosc_probs;

  def process(self, data):
    data["vals"] = []
    for i, v in enumerate(data["ADCs"]):
      if i < len(self.param_maps):
        data["vals"].append(self.param_maps[i](v))

    Es, osc_probs, bosc_probs = self.calc_probs(data["vals"])
    data["osc_probs"] = {}
    data["osc_probs"]["numu"] = [ [Es[i], osc_probs[i][1][1], bosc_probs[i][1][1]] for i in range(len(osc_probs))]
    data["osc_probs"]["nue"] = [ [Es[i], osc_probs[i][1][0], bosc_probs[i][1][0]] for i in range(len(osc_probs))]
    return data

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
