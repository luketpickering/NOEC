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
from scipy.stats import norm

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
    self.length = 1300
    

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
    self.noise = [[random.uniform(0.9,1.1) for i in range(self.true_bin_num)] for i in range(3)]
    self.calc_true_events()
    self.true_Es_disp, self.true_mu_events_disp, self.true_e_events_disp, self.true_e_bevents_disp = self.true_Es, self.true_mu_events, self.true_e_events, self.true_e_bevents
    
    self.ml_numu_events = [0 for i in range(self.true_bin_num)]
    self.ml_nue_events = [0 for i in range(self.true_bin_num)]
    self.ml_nue_bevents = [0 for i in range(self.true_bin_num)]
    self.ml_Es= np.linspace(0.5,6.4,self.true_bin_num)
    self.ml_lh = 0
    self.ml_walker_pos = [[0,0,0] for _ in range(10)]
    self.ml_grad_desc_vals = [0,0,0]

  def calc_true_events(self):
    self.true_Es, self.true_mu_events, self.true_e_events, self.true_e_bevents = self.calc_events(self.true_vals_mapped,self.length, self.true_bin_num)
    self.mu_noise = np.array([self.noise[0][i] * self.true_mu_events[i] for i in range(len(self.true_mu_events))])
    self.e_noise = np.array([self.noise[1][i] * self.true_e_events[i] for i in range(len(self.true_e_events))])
    self.e_bnoise = np.array([self.noise[2][i] * self.true_e_bevents[i] for i in range(len(self.true_e_bevents))])
    
    
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
    return Es ,mu_osc_probs,e_osc_probs,e_bosc_probs
  
  def calc_events(self, vals, L, num_bins, flux_loc = 2, flux_scale=1, nu_num=100):
    Es = np.linspace(0.5,6.4,num_bins) #GeV
    flux = norm.pdf(Es, flux_loc, flux_scale)
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

    mu_osc_probs =np.array([osc_probs[i][1][1] for i in range(len(osc_probs))])*flux*nu_num
    e_osc_probs = np.array([osc_probs[i][1][0] for i in range(len(osc_probs))])*flux*nu_num
    e_bosc_probs = np.array([bosc_probs[i][1][0] for i in range(len(bosc_probs))])*flux*nu_num
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
      return np.sum((predicted -actual)**2/actual)/2

  def calc_lh_disp(self, predicted,actual):
    return round(100/np.exp(self.calculate_likelihood(predicted,actual)/2),0)

  def slow_data(self,noise, flux=100):
    actual_mu_events = copy.deepcopy(self.true_mu_events_disp)
    actual_e_events = copy.deepcopy(self.true_e_events_disp)
    actual_e_bevents = copy.deepcopy(self.true_e_bevents_disp)
    for i in range(len(self.true_mu_events_disp)):
       self.true_mu_events_disp[i] = 0.0000000001
       self.true_e_events_disp[i] = 0.0000000001
       self.true_e_bevents_disp[i] = 0.0000000001
    iters_without_hit = 0
    while iters_without_hit <250:
      particle = random.randint(0,2)
      bin = random.randint(0,len(self.true_mu_events_disp)-1)
      if particle == 0:
        change = min(random.uniform(0.05,0.2)*flux,actual_mu_events[bin])
        actual_mu_events[bin] -= change
        self.true_mu_events_disp[bin] += change
      elif particle == 1:
        change = min(random.uniform(0.005,0.02)*flux,actual_e_events[bin])
        actual_e_events[bin] -= change
        self.true_e_events_disp[bin] += change
      else:
        change = min(random.uniform(0.005,0.01)*flux,actual_e_bevents[bin])
        actual_e_bevents[bin] -= change
        self.true_e_bevents_disp[bin] += change
      if change == 0:
        iters_without_hit +=1
      else:
        iters_without_hit = 0
      time.sleep(0.1)
    self.set_true_disp(noise)

  def ml_probs_func_display(self,a):
    mapped_vals = []
    for i, v in enumerate(a):
      if i < len(self.param_maps):
        mapped_vals.append(self.param_maps[i](v))
    Es, mu_osc_probs,e_osc_probs,e_bosc_probs = self.calc_events(mapped_vals,self.length, self.true_bin_num)
    return Es, mu_osc_probs, e_osc_probs,e_bosc_probs

  def mcmc_take_step(self,current, prob_func):
    step = [ np.random.normal(c, 100) for c in current]
    if prob_func(step) > prob_func(current):
        return step
    elif prob_func(step) == -np.inf:
      return current
    else:
        accept_threshold = prob_func(current)/prob_func(step)
        if np.random.rand() < accept_threshold:
            return step
        else:
            return current

  def log_uniform_prior(self,params):
    Dm32, Th23, dcp = params
    if 0 <= Dm32 <= 1024 and 0<=Th23 <=1024 and 0 <= dcp <= 1024:
        return 0
    return -np.inf
  
  def ml_mcmc(self, time_iter=0.1, noise=False, num_walkers = 10):
     time.sleep(2)
     fitting_Es = copy.deepcopy(self.true_Es_disp)
     poster_func =  lambda x: -self.calculate_likelihood(self.ml_probs_func_display(x)[2],self.true_e_events_disp) + self.log_uniform_prior(x)
     vals = [[[random.randint(0,1024) for _ in range(3)]] for j in range(num_walkers)]
     posts = [0 for i in range(num_walkers)]
     avg_lh = 0
     while avg_lh < 85  or  self.ml_lh < 98:
       for j in range(num_walkers):
         posts[j] = poster_func(vals[j][-1])
         vals[j].append(self.mcmc_take_step(vals[j][-1], poster_func))
       ml_walker_pos = [vals[k][-1] for k in range(num_walkers)]
       for j in range(len(ml_walker_pos)):
         for ii, v in enumerate(ml_walker_pos[j]):
           if ii < len(self.param_maps):
             self.ml_walker_pos[j][ii] =self.param_maps[ii](v)
       best_walk = posts.index(max(posts))
       avg_lh = np.sum([self.ml_lh_disp(vals[i][-1]) for i in range(num_walkers)])/num_walkers
       self.ml_Es, self.ml_numu_events, self.ml_nue_events, self.ml_nue_bevents = self.ml_probs_func_display(vals[best_walk][-1])
       self.ml_lh = round(avg_lh)
       time.sleep(time_iter)
     

  def ml_fit_to_true(self, time_iter=0.1, noise=False):
    time.sleep(2)
    fitting_Es = copy.deepcopy(self.true_Es_disp)
    currentVals = [random.randint(0,1024) for i in range(4)]
    learning_step = 1000
    steps = 0
    while self.ml_lh <100 or (steps <500 and self.ml_lh<95):
      time.sleep(time_iter)
      if steps >600 :
        currentVals = [random.randint(0,1024) for i in range(4)]
        steps = 0
      cost_grad = self.get_gradient(self.cost,currentVals)
      for i in range(len(currentVals)):
        currentVals[i] -= learning_step*cost_grad[i]
        if currentVals[i] > 1023:
          currentVals[i] = 1023
        elif currentVals[i] < 1:
          currentVals[i] = 1
      steps += 1
      self.ml_Es, self.ml_numu_events, self.ml_nue_events, self.ml_nue_bevents = self.ml_probs_func_display(currentVals)
      self.ml_lh = self.ml_lh_disp(currentVals)
      self.ml_grad_desc_vals = currentVals
      
      
      

  def cost(self,a):
    mapped_vals = []
    for i,v in enumerate(a):
      if i < len(self.param_maps):
        mapped_vals.append(self.param_maps[i](v))
    if len(self.true_Es_disp) == self.true_bin_num:
      Es, mu_osc_events,e_osc_events,e_bosc_events  = self.calc_events(mapped_vals,self.length,  self.true_bin_num)
    return (self.calculate_likelihood(e_osc_events,self.true_e_events_disp) + self.calculate_likelihood(e_bosc_events,self.true_e_bevents_disp))/2


  def ml_lh_disp(self,a):
    mapped_vals = []
    for i,v in enumerate(a):
      if i < len(self.param_maps):
        mapped_vals.append(self.param_maps[i](v))
    if len(self.true_Es_disp) == self.true_bin_num:
      Es, mu_osc_events,e_osc_events,e_bosc_events  = self.calc_events(mapped_vals,self.length,  self.true_bin_num)
    return self.calc_lh_disp(e_osc_events,self.true_e_events_disp)

  def get_gradient(self,cost_func, vals, h=1e-7):
    gradients = []
    for i in range(len(vals)):
        lowerGrad = vals.copy()
        lowerGrad[i] -= h
        upperGrad = vals.copy()
        upperGrad[i] += h
        gradients.append((cost_func(upperGrad)-cost_func(lowerGrad))/(2*h))
    return np.array(gradients)
      
      

  def is_setting_changed(self,noise):
    return self.previous_noise != noise

  def set_true_disp(self,noise):
    if noise:
      self.true_mu_events_disp, self.true_e_events_disp, self.true_e_bevents_disp = self.mu_noise, self.e_noise     , self.e_bnoise
    else:
      self.true_mu_events_disp, self.true_e_events_disp, self.true_e_bevents_disp = self.true_mu_events, self.true_e_events, self.true_e_bevents

  def process(self, data):
    if (abs(self.length-round(data['L_km']/1023*2000)) > 20):
      self.length = round(data['L_km']/1023*2000)
    self.calc_true_events()
    #print(data)
    data["vals"] = []
    data['hist'] = True
    #print(data["ADCs"])
    for i, v in enumerate(data["ADCs"]):
      if i < len(self.param_maps):
        if data["ADCStates"][i]:
          data["vals"].append(self.param_maps[i](v))
        else:
          data["vals"].append(self.true_vals_mapped[i])
    #print(data["vals"])
    data["L_km"] = self.length
    data["start_ml"] =True

    data ["time_sent"] = time.time();

    
    Es, mu_osc_probs,e_osc_probs,e_bosc_probs = self.calc_probs(data["vals"], self.length)
    Es_ev, mu_osc_events, e_osc_events, e_bosc_events = self.calc_events(data["vals"], self.length, self.true_bin_num)
    data["osc_probs"] = {}
    data["osc_events"] = {}
    

    if self.load_thread == None or not self.load_thread.is_alive():
      self.set_true_disp(data['noise'])

    if len(self.true_Es_disp) == self.true_bin_num:
      Es_lh, mu_osc_probs_lh,e_osc_probs_lh,e_bosc_probs_lh = self.calc_events(data["vals"], self.length, self.true_bin_num)
    else:
      Es_lh, mu_osc_probs_lh,e_osc_probs_lh,e_bosc_probs_lh = Es, mu_osc_probs,e_osc_probs,e_bosc_probs
  
    if data["slow_load"]:
      if self.load_thread == None:
        print("Thread started")
        self.load_thread = threading.Thread(target = self.slow_data, args=(data['noise'],))
        self.load_thread.start()
    data["ml_mode"] = "MCMC" 
        
    if data["start_ml"]:       
      if self.ml_thread == None or (not self.ml_thread.is_alive()) and self.is_setting_changed(data["noise"]):
        print("Thread started")
        if data['ml_mode'] == "MCMC":
          self.ml_thread = threading.Thread(target=self.ml_mcmc)
        else:
          self.ml_thread = threading.Thread(target = self.ml_fit_to_true)
        self.ml_thread.start()
        data["ml_status"] = "In Progress"
      elif not self.ml_thread.is_alive():
        data['ml_status'] = "Complete"
      else:
        data["ml_status"] = "In Progress"
        
      data["osc_probs"]["mlnumu"] = [ [self.ml_Es[i], self.ml_numu_events[i]] for i in range(len(self.ml_numu_events))]
      data["osc_probs"]["mlnue"] = [ [self.ml_Es[i], self.ml_nue_events[i]] for i in range(len(self.ml_nue_events))]
      data["osc_probs"]["mlnueb"] = [ [self.ml_Es[i], self.ml_nue_bevents[i]] for i in range(len(self.ml_nue_bevents))]
      data["ml_likelihood"] = self.ml_lh
      data["ml_walker_pos"] = [[[self.ml_walker_pos[i][1], self.ml_walker_pos[i][0]] for i in range(len(self.ml_walker_pos))],[[self.ml_walker_pos[i][2], self.ml_walker_pos[i][0]] for i in range(len(self.ml_walker_pos))],[[self.ml_walker_pos[i][2], self.ml_walker_pos[i][1]] for i in range(len(self.ml_walker_pos))]]

    data["osc_probs"]["numu"] = [ [Es[i], mu_osc_probs[i]] for i in range(len(Es))]
    data["osc_probs"]["nue"] = [ [Es[i], e_osc_probs[i]] for i in range(len(Es))]
    data["osc_probs"]["bnue"] = [ [Es[i], e_bosc_probs[i]] for i in range(len(Es))]
    data["osc_events"]["numu_true"] = [[self.true_Es_disp[i], self.true_mu_events_disp[i]] for i in range(len(self.true_Es_disp))]
    data["osc_events"]["nue_true"] = [[self.true_Es_disp[i], self.true_e_events_disp[i]] for i in range(len(self.true_Es_disp))]
    data["osc_events"]["bnue_true"] = [[self.true_Es_disp[i], self.true_e_bevents_disp[i]] for i in range(len(self.true_Es_disp))]
    data["osc_events"]["numu"] = [[Es_ev[i], mu_osc_events[i]] for i in range(len(Es_ev))]
    data["osc_events"]["nue"] = [[Es_ev[i], e_osc_events[i]] for i in range(len(Es_ev))]
    data["osc_events"]["bnue"] = [[Es_ev[i], e_bosc_events[i]] for i in range(len(Es_ev))]
    data["osc_probs"]["likelihood"] = self.calc_lh_disp(e_osc_events, self.true_e_events_disp)
    data["osc_probs"]["score_likelihood"] = round((self.calc_lh_disp(mu_osc_events, self.true_mu_events) + self.calc_lh_disp(e_osc_events, self.true_e_events) + self.calc_lh_disp(e_bosc_events, self.true_e_bevents))/3)
    data["trans_prob_max"] = self.calc_state_probs(int(data["tick"]), data["vals"], data["L_km"])

    data["ml_grad_desc_vals"] = []
    for i, v in enumerate(self.ml_grad_desc_vals):
      if i < len(self.param_maps):
          data["ml_grad_desc_vals"].append(self.param_maps[i](v))
    

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
