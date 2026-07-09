#!/usr/bin/env python3

import json
import yaml
import asyncio
import sys
import copy

from websockets.asyncio.server import serve

from noec_host import NOECHost

from nufast import Probability_Matter_LBL

from math import pow, sin, pi
from scipy import optimize

import numpy as np
import random
import threading
import time

class InputProcessor:
  def __init__(self, cfg):
    self.cfg = cfg

    self.param_maps = []
    self.param_idx = {}
    self.load_thread = None
    self.ml_thread = None
    

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
    self.true_vals_mapped = []
    for i, v in enumerate(true_vals):
      if i < len(self.param_maps):
       self. true_vals_mapped.append(self.param_maps[i](v))
    self.true_bin_num = 30
    self.true_Es, self.true_osc_probs, self.true_bosc_probs = self.calc_probs_hist(self.true_vals_mapped,1300,  self.true_bin_num)
    self.e_noise = np.array([random.uniform(-0.1,0.1)*i[1][0] for i in self.true_osc_probs])
    self.e_bnoise = np.array([random.uniform(-0.1,0.1)*i[1][0] for i in self.true_bosc_probs])
    self.mu_noise = np.array([random.uniform(-0.1,0.1)*i[1][1] for i in self.true_osc_probs])
    self.ml_nue_probs = [0 for i in range(self.true_bin_num)]
    
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
  
  def calc_probs_hist(self, vals, L, num_bins, correct_for_disp=True):
    Es = np.linspace(0.5,6.4,num_bins) #GeV
    #print("Es:", Es) 
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
    bin_width = Es[1]-Es[0]
    Es -= (bin_width/2)
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
    try:
      return np.sum(np.power(predicted -actual ,2)/actual)
    except:
      return 0

  def calc_lh_disp(self, predicted,actual):
    return round(100/np.exp(self.calculate_likelihood(predicted,actual)),0)

  def slow_data(self):
    actual_osc_probs = copy.deepcopy(self.true_osc_probs)
    actual_bosc_probs = copy.deepcopy(self.true_bosc_probs)
    for i in range(self.true_bin_num):
       self.true_osc_probs[i][1][0] = 0.0000000001
       self.true_osc_probs[i][1][1] = 0.0000000001
       self.true_bosc_probs[i][1][0] = 0.0000000001
    print(self.true_osc_probs)
    iters_without_hit = 0
    while iters_without_hit <250:
      print(iters_without_hit)
      particle = random.randint(0,2)
      bin = random.randint(0,self.true_bin_num-1)
      if particle == 0:
        change = min(random.uniform(0.05,0.2),actual_osc_probs[bin][1][1])
        print(change)
        actual_osc_probs[bin][1][1] -= change
        self.true_osc_probs[bin][1][1] += change
        print(self.true_osc_probs[bin][1][1])
      elif particle == 1:
        change = min(random.uniform(0.005,0.02),actual_osc_probs[bin][1][0])
        print(change)
        actual_osc_probs[bin][1][0] -= change
        self.true_osc_probs[bin][1][0] += change
        print(self.true_osc_probs[bin][1][0])
      else:
        change = min(random.uniform(0.005,0.01),actual_bosc_probs[bin][1][0])
        print(change)
        actual_bosc_probs[bin][1][0] -= change
        self.true_bosc_probs[bin][1][0] += change
        print(self.true_bosc_probs[bin][1][0])
      if change == 0:
        iters_without_hit +=1
      else:
        iters_without_hit = 0
      time.sleep(0.1)
    self.true_Es, self.true_osc_probs, self.true_bosc_probs = self.calc_probs_hist(self.true_vals_mapped,1300,  self.true_bin_num)
    
    


  def ml_probs_func(self,Es, a, b,c,d):
    mapped_vals = []
    for i, v in enumerate([a,b,c,d]):
      if i < len(self.param_maps):
       mapped_vals.append(self.param_maps[i](v))
    Es, osc_probs, bosc_probs = self.calc_probs_hist(mapped_vals,1300,  self.true_bin_num)
    return np.array([osc_probs[i][1][0] for i in range(len(osc_probs))])

  def ml_probs_func_display(self,a,b,c,d):
    mapped_vals = []
    for i, v in enumerate([a,b,c,d]):
      if i < len(self.param_maps):
        mapped_vals.append(self.param_maps[i](v))
    Es, osc_probs, bosc_probs = self.calc_probs(mapped_vals,1300)
    return np.array([osc_probs[i][1][0] for i in range(len(osc_probs))])

  def ml_fit_to_true(self,time_iter=1, noise = False):
    intermediate_params = []
    p0 = [random.randint(0,1044) for i in range(4)]
    params, cov = optimize.curve_fit(self.ml_probs_func, self.true_Es,np.array([self.true_osc_probs[i][1][0] for i in range(len(self.true_osc_probs))]), p0,method="trf", callback=(lambda x: intermediate_params.append(x)))
    #intermediate_params = [[random.randint(0,1044) for i in range(len(p0))] for j in range(random.randint(10,30))]
    for i in intermediate_params:
      print(i)
      self.ml_nue_probs = self.ml_probs_func_display(*i)
      time.sleep(time_iter)

  def hist_view(self):
    pass

  def add_noise(self):
    pass

  def remove_noise(self):
    pass 

  def curve_view(self):
    pass

  def process(self, data):
    print(data)
    #print(data)
    data["vals"] = []
    #print(data["ADCs"])
    for i, v in enumerate(data["ADCs"]):
      if i < len(self.param_maps):
        data["vals"].append(self.param_maps[i](v))
    #print(data["vals"])
    data["L_km"] = 1300
    
    Es, osc_probs, bosc_probs = self.calc_probs(data["vals"], data["L_km"])
    Es_h, osc_probs_h, bosc_probs_h = self.calc_probs_hist(data["vals"], data["L_km"], self.true_bin_num)
    data["osc_probs"] = {}

    
  
    if data["slow_load"]:
      if self.load_thread == None:
        print("Thread started")
        self.load_thread = threading.Thread(target = self.slow_data)
        self.load_thread.start()
        
    if data["start_ml"]:       
      if self.ml_thread == None:
        print("Thread started")
        self.ml_thread = threading.Thread(target = self.ml_fit_to_true)
        self.ml_thread.start()
      data["osc_probs"]["mlnue"] = [ [Es[i], self.ml_nue_probs[i]] for i in range(len(self.ml_nue_probs))]

    data["osc_probs"]["numu"] = [ [Es[i], osc_probs[i][1][1]] for i in range(len(osc_probs))]
    data["osc_probs"]["nue"] = [ [Es[i], osc_probs[i][1][0]] for i in range(len(osc_probs))]
    data["osc_probs"]["bnue"] = [ [Es[i], bosc_probs[i][1][0]] for i in range(len(osc_probs))]

    if data["noise"]:
      data["osc_probs"]["numu_true"] = [ [self.true_Es[i], self.true_osc_probs[i][1][1]+self.mu_noise[i]] for i in range(len(self.true_osc_probs))]
      data["osc_probs"]["nue_true"] = [ [self.true_Es[i], self.true_osc_probs[i][1][0]+self.e_noise[i]] for i in range(len(self.true_osc_probs))]
      data["osc_probs"]["bnue_true"] = [ [self.true_Es[i], self.true_bosc_probs[i][1][0] + self.e_bnoise[i]] for i in range(len(self.true_osc_probs))]
      data["osc_probs"]["likelihood"] = self.calc_lh_disp(np.array([osc_probs_h[i][1][0] for i in range(len(osc_probs_h))]),np.array([data["osc_probs"]["nue_true"][i][1] +self.e_noise[i] for i in range(len(self.true_osc_probs))]))
    else:
      data["osc_probs"]["numu_true"] = [ [self.true_Es[i], self.true_osc_probs[i][1][1]] for i in range(len(self.true_osc_probs))]
      data["osc_probs"]["nue_true"] = [ [self.true_Es[i], self.true_osc_probs[i][1][0]] for i in range(len(self.true_osc_probs))]
      data["osc_probs"]["bnue_true"] = [ [self.true_Es[i], self.true_bosc_probs[i][1][0]] for i in range(len(self.true_osc_probs))]
      data["osc_probs"]["likelihood"] = self.calc_lh_disp(np.array([osc_probs_h[i][1][0] for i in range(len(osc_probs_h))]),np.array([data["osc_probs"]["nue_true"][i][1]for i in range(len(self.true_osc_probs))]))
    data["osc_probs"]["true_likelihood"] = data["osc_probs"]["likelihood"]
    data["trans_prob_max"] = self.calc_state_probs(int(data["tick"]), data["vals"], data["L_km"])
  
   # print(data["osc_probs"]["likelihood"])
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
