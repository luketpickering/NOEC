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
    self.prev_noise = False
    self.prev_hist = False
    

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

    true_vals = [random.randint(0,int(adcmx)) for i in range(4)]
    self.true_vals_mapped = []
    for i, v in enumerate(true_vals):
      if i < len(self.param_maps):
       self. true_vals_mapped.append(self.param_maps[i](v))
    self.true_bin_num = 30

    self.true_Es, self.true_mu_probs, self.true_e_probs, self.true_e_bprobs = self.calc_probs(self.true_vals_mapped,1300)
    self.true_Es_hist, self.true_mu_probs_hist, self.true_e_probs_hist, self.true_e_bprobs_hist = self.calc_probs_hist(self.true_vals_mapped,1300,  self.true_bin_num)

    self.e_noise = np.array([random.uniform(0.9,1.1)*i for i in self.true_e_probs])
    self.e_bnoise = np.array([random.uniform(0.9,1.1)*i for i in self.true_e_bprobs])
    self.mu_noise = np.array([random.uniform(0.9,1.1)*i for i in self.true_mu_probs])

    self.e_noise_hist = np.array([random.uniform(0.9,1.1)*i for i in self.true_e_probs_hist])
    self.e_bnoise_hist = np.array([random.uniform(0.9,1.1)*i for i in self.true_e_bprobs_hist])
    self.mu_noise_hist = np.array([random.uniform(0.9,1.1)*i for i in self.true_mu_probs_hist])
    
    self.true_Es_disp, self.true_mu_probs_disp, self.true_e_probs_disp, self.true_e_bprobs_disp = self.true_Es, self.true_mu_probs, self.true_e_probs, self.true_e_bprobs
    
    self.ml_nue_probs = [0 for i in range(100)]
    self.ml_Es = np.logspace(-0.3,0.8,100)
    self.ml_lh = 0
    
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
    mu_osc_probs = np.array([osc_probs[i][1][1] for i in range(len(osc_probs))])
    e_osc_probs = np.array([osc_probs[i][1][0] for i in range(len(osc_probs))])
    e_bosc_probs = np.array([bosc_probs[i][1][0] for i in range(len(bosc_probs))])
    return Es, mu_osc_probs,e_osc_probs,e_bosc_probs
  
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

    mu_osc_probs =np.array([osc_probs[i][1][1] for i in range(len(osc_probs))])
    e_osc_probs = np.array([osc_probs[i][1][0] for i in range(len(osc_probs))])
    e_bosc_probs = np.array([bosc_probs[i][1][0] for i in range(len(bosc_probs))])
    return Es, mu_osc_probs,e_osc_probs,e_bosc_probs

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
      return np.sum((predicted -actual)**2/actual)

  def calc_lh_disp(self, predicted,actual):
    return round(100/np.exp(self.calculate_likelihood(predicted,actual)/2),0)

  def slow_data(self,hist, noise):
    actual_mu_probs = copy.deepcopy(self.true_mu_probs_disp)
    actual_e_probs = copy.deepcopy(self.true_e_probs_disp)
    actual_e_bprobs = copy.deepcopy(self.true_e_bprobs_disp)
    for i in range(len(self.true_mu_probs_disp)):
       self.true_mu_probs_disp[i] = 0.0000000001
       self.true_e_probs_disp[i] = 0.0000000001
       self.true_e_bprobs_disp[i] = 0.0000000001
    iters_without_hit = 0
    while iters_without_hit <250:
      print(iters_without_hit)
      particle = random.randint(0,2)
      bin = random.randint(0,len(self.true_mu_probs_disp)-1)
      if particle == 0:
        change = min(random.uniform(0.05,0.2),actual_mu_probs[bin])
        actual_mu_probs[bin] -= change
        self.true_mu_probs_disp[bin] += change
      elif particle == 1:
        change = min(random.uniform(0.005,0.02),actual_e_probs[bin])
        actual_e_probs[bin] -= change
        self.true_e_probs_disp[bin] += change
      else:
        change = min(random.uniform(0.005,0.01),actual_e_bprobs[bin])
        actual_e_bprobs[bin] -= change
        self.true_e_bprobs_disp[bin] += change
      if change == 0:
        iters_without_hit +=1
      else:
        iters_without_hit = 0
      time.sleep(0.1)
    self.set_true_disp(hist,noise)
    


  def ml_probs_func_sp(self,Es, a, b,c,d):
    mapped_vals = []
    for i, v in enumerate([a,b,c,d]):
      if i < len(self.param_maps):
       mapped_vals.append(self.param_maps[i](v))
    if len(Es) == self.true_bin_num:
      Es, mu_osc_probs,e_osc_probs,e_bosc_probs  = self.calc_probs_hist(mapped_vals,1300,  self.true_bin_num)
    else:
      Es, mu_osc_probs,e_osc_probs,e_bosc_probs  = self.calc_probs(mapped_vals,1300)
    return e_osc_probs

  def ml_probs_func_display(self,a):
    mapped_vals = []
    for i, v in enumerate(a):
      if i < len(self.param_maps):
        mapped_vals.append(self.param_maps[i](v))
    Es, mu_osc_probs,e_osc_probs,e_bosc_probs = self.calc_probs(mapped_vals,1300)
    return Es, e_osc_probs

  def ml_fit_to_true_sp(self,time_iter=1, noise = False):
    fitting_Es = copy.deepcopy(self.true_Es_disp)
    fitting_e_probs = copy.deepcopy(self.true_e_probs_disp)
    intermediate_params = []
    p0 = [random.randint(0,1044) for i in range(4)]
    params, cov = optimize.curve_fit(self.ml_probs_func, fitting_Es,fitting_e_probs, p0,method="trf", callback=(lambda x: intermediate_params.append(x)))
    for i in intermediate_params:
      self.ml_lh = self.calc_lh_disp(self.ml_probs_func(fitting_Es,*i), fitting_e_probs)
      self.ml_Es, self.ml_nue_probs = self.ml_probs_func_display(*i)
      time.sleep(time_iter)

  def ml_fit_to_true(self, time_iter=0.1, noise=False):
    time.sleep(2)
    fitting_Es = copy.deepcopy(self.true_Es_disp)
    currentVals = [random.randint(0,1044) for i in range(4)]
    learning_step = 10000
    steps = 0
    print("likelihood",self.ml_lh)
    while self.ml_lh <100 or (steps <500 and self.ml_lh<95):
      time.sleep(time_iter)
      if steps >600 :
        currentVals = [random.randint(0,1044) for i in range(4)]
        steps = 0
      cost_grad = self.get_gradient(self.cost,currentVals)
      for i in range(len(currentVals)):
        currentVals[i] -= learning_step*cost_grad[i]
        if currentVals[i] > 1043:
          currentVals[i] = 1043
        elif currentVals[i] < 1:
          currentVals[i] = 1
      steps += 1
      self.ml_Es, self.ml_nue_probs = self.ml_probs_func_display(currentVals)
      self.ml_lh = self.ml_lh_disp(currentVals)
      
      
      

  def cost(self,a):
    mapped_vals = []
    for i,v in enumerate(a):
      if i < len(self.param_maps):
        mapped_vals.append(self.param_maps[i](v))
    if len(self.true_Es_disp) == self.true_bin_num:
      Es, mu_osc_probs,e_osc_probs,e_bosc_probs  = self.calc_probs_hist(mapped_vals,1300,  self.true_bin_num)
    else:
      Es, mu_osc_probs,e_osc_probs,e_bosc_probs  = self.calc_probs(mapped_vals,1300)
    return (self.calculate_likelihood(e_osc_probs,self.true_e_probs_disp) + self.calculate_likelihood(e_bosc_probs,self.true_e_bprobs_disp))/2


  def ml_lh_disp(self,a):
    mapped_vals = []
    for i,v in enumerate(a):
      if i < len(self.param_maps):
        mapped_vals.append(self.param_maps[i](v))
    if len(self.true_Es_disp) == self.true_bin_num:
      Es, mu_osc_probs,e_osc_probs,e_bosc_probs  = self.calc_probs_hist(mapped_vals,1300,  self.true_bin_num)
    else:
      Es, mu_osc_probs,e_osc_probs,e_bosc_probs  = self.calc_probs(mapped_vals,1300)
    return self.calc_lh_disp(e_osc_probs,self.true_e_probs_disp)

  def get_gradient(self,cost_func, vals, h=1e-7):
    gradients = []
    print(vals)
    for i in range(len(vals)):
        lowerGrad = vals.copy()
        lowerGrad[i] -= h
        upperGrad = vals.copy()
        upperGrad[i] += h
        gradients.append((cost_func(upperGrad)-cost_func(lowerGrad))/(2*h))
    return np.array(gradients)
      
      

  def is_setting_changed(self,noise,hist):
    return self.previous_noise != noise or self.previous_hist!= hist

  def set_true_disp(self, hist, noise):
    if hist:
      self.true_Es_disp = self.true_Es_hist
      if noise:
        self.true_mu_probs_disp, self.true_e_probs_disp, self.true_e_bprobs_disp = self.mu_noise_hist, self.e_noise_hist, self.e_bnoise_hist
      else:
        self.true_mu_probs_disp, self.true_e_probs_disp, self.true_e_bprobs_disp = self.true_mu_probs_hist, self.true_e_probs_hist, self.true_e_bprobs_hist
    else:
      self.true_Es_disp = self.true_Es
      if noise:
        self.true_mu_probs_disp, self.true_e_probs_disp, self.true_e_bprobs_disp = self.mu_noise, self.e_noise, self.e_bnoise
      else:
        self.true_mu_probs_disp, self.true_e_probs_disp, self.true_e_bprobs_disp = self.true_mu_probs, self.true_e_probs, self.true_e_bprobs

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
    data["start_ml"] = True
    data["slow_load"] = True
    data["hist"] = True
    data["noise"] = False
    load_hist = None
    
    Es, mu_osc_probs,e_osc_probs,e_bosc_probs = self.calc_probs(data["vals"], data["L_km"])
    data["osc_probs"] = {}
    

    if self.load_thread == None or not self.load_thread.is_alive():
      self.set_true_disp(data['hist'], data['noise'])

    if len(self.true_Es_disp) == self.true_bin_num:
      print("hist")
      Es_lh, mu_osc_probs_lh,e_osc_probs_lh,e_bosc_probs_lh = self.calc_probs_hist(data["vals"], data["L_km"], self.true_bin_num)
    else:
      Es_lh, mu_osc_probs_lh,e_osc_probs_lh,e_bosc_probs_lh = Es, mu_osc_probs,e_osc_probs,e_bosc_probs
  
    if data["slow_load"]:
      if self.load_thread == None:
        print("load_hist", load_hist)
        self.prev_hist = data["hist"]
        print("Thread started")
        self.load_thread = threading.Thread(target = self.slow_data, args=(data['hist'], data['noise']))
        self.load_thread.start()
      data["hist"] = self.prev_hist
        
    if data["start_ml"]:       
      if self.ml_thread == None or (not self.ml_thread.is_alive()) and self.is_setting_changed(data["noise"],data["hist"]):
        print("Thread started")
        self.ml_thread = threading.Thread(target = self.ml_fit_to_true)
        self.ml_thread.start()
        data["ml_status"] = "In Progress"
      elif not self.ml_thread.is_alive():
        data['ml_status'] = "Complete"
      else:
        data["ml_status"] = "In Progress"

      data["osc_probs"]["mlnue"] = [ [self.ml_Es[i], self.ml_nue_probs[i]] for i in range(len(self.ml_nue_probs))]
      data["ml_likelihood"] = self.ml_lh
      print(data["ml_likelihood"])
      #for i in range(30):
        #print(self.true_osc_probs[i][1][0], data["osc_probs"]["mlnue"][i][1],(self.true_osc_probs[i][1][0]- data["osc_probs"]["mlnue"][i][1])**2/self.true_osc_probs[i][1][0])
      #print(self.calculate_likelihood(np.array([data["osc_probs"]["mlnue"][i][1] for i in range(len(data["osc_probs"]["mlnue"]))]),np.array([self.true_osc_probs[i][1][0]for i in range(len(self.true_osc_probs))])))

    data["osc_probs"]["numu"] = [ [Es[i], mu_osc_probs[i]] for i in range(len(Es))]
    data["osc_probs"]["nue"] = [ [Es[i], e_osc_probs[i]] for i in range(len(Es))]
    data["osc_probs"]["bnue"] = [ [Es[i], e_bosc_probs[i]] for i in range(len(Es))]
    data["osc_probs"]["numu_true"] = [[self.true_Es_disp[i], self.true_mu_probs_disp[i]] for i in range(len(self.true_Es_disp))]
    data["osc_probs"]["nue_true"] = [[self.true_Es_disp[i], self.true_e_probs_disp[i]] for i in range(len(self.true_Es_disp))]
    data["osc_probs"]["bnue_true"] = [[self.true_Es_disp[i], self.true_e_bprobs_disp[i]] for i in range(len(self.true_Es_disp))]
    data["osc_probs"]["likelihood"] = self.calc_lh_disp(e_osc_probs_lh, self.true_e_probs_disp)
    data["osc_probs"]["score_likelihood"] = self.calc_lh_disp(e_osc_probs, self.true_e_probs)
    data["trans_prob_max"] = self.calc_state_probs(int(data["tick"]), data["vals"], data["L_km"])

    self.previous_hist = data["hist"]
    self.previous_noise = data["noise"]

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
