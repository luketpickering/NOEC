#! /usr/bin/env python3

from nicegui import ui, run, Event

from multiprocessing import Process, Queue
from noec_host import monitor_serial

from math import pi, pow

from nufast import Probability_Matter_LBL

import numpy as np

import sys

import datetime

resultq = None
monitorproc = None
timeout = None

new_vals_available = Event[dict]()

async def poll_new_vals():
  global resultq, monitorproc, timeout

  if monitorproc is None:
    resultq = Queue()
    monitorproc = Process(target=monitor_serial, args=(resultq, sys.argv[1]))
    monitorproc.start()

  try:
    vals = await run.io_bound(resultq.get)

    print(f"[MAIN] Updated values: {vals}")
  except Exception as e:
    monitorproc.kill()
    raise e

  if vals:
    new_vals_available.emit(vals)

  timeout = 10 # first invocation we don't timeout to wait for the serial
              #   connection to start, then expect updates

ui.timer(0.05, poll_new_vals) # poll for new values


toDM32 = lambda x: (2.1 + ((2.7-2.1) * (float(x)/255.0)))
toth23 = lambda x: (0.4 + ((0.7-0.4) * (float(x)/255.0)))
todcp = lambda x: (2 * (float(x)/255.0))
converters = [toDM32,toth23,todcp]
labels = [r"$\Delta{}m^{2}_{32}\ \times10^{-3}\mathrm{eV}$",r"$sin^{2}\left(\theta_{23}\right)$",r"$\delta_{cp}$"]

columns = [
    {'name': 'name', 'label': 'Parameter', 'field': 'pname', 'required': True, 'align': 'left'},
    {'name': 'value', 'label': 'Value', 'field': 'pval'},
]
rows = [
    {'pname': 'Dm_32 x10^{3} eV'},
    {'pname': 'sin^2(th23)'},
    {'pname': 'dcp/pi'},
]
tbl = ui.table(columns=columns, rows=rows, row_key='name')

def tbl_update(vals):
  for i, v in enumerate(vals):
    tbl.rows[i]['pval'] = "{:.3g}".format(converters[i](v))

class valtrace:
  def __init__(self, validx):
    self.x = []
    self.y = []

    self.validx = validx

    self.fig = ui.matplotlib(figsize=(3, 2)).figure
    self.vmap = converters[validx]
    self.label = labels[validx]

    with self.fig:
      self.fig.gca().plot(self.x, self.y, '-')
      self.fig.tight_layout()

  def update(self, vals):
    if len(self.x):
      self.x.append(self.x[-1]+1)
    else:
      self.x.append(0)

    self.y.append(self.vmap(vals[self.validx]))

    if len(self.x) > 100:
      self.x = self.x[-100:]
      self.y = self.y[-100:]

    with self.fig:
      self.fig.clf()
      self.fig.gca().plot(self.x, self.y, '-')
      self.fig.gca().set_ylim([self.vmap(0),self.vmap(255*1.2)])
      self.fig.gca().set_ylabel(self.label)
      self.fig.gca().set_xlabel("tick")

with ui.row():
  valtraces = [valtrace(i) for i in range(3)]

class oscprob:
  def __init__(self, maxy):
    self.fig = ui.matplotlib(figsize=(6, 4)).figure
    self.maxy = maxy

    with self.fig:
      self.fig.tight_layout()

  def update(self, x, y, by, iy, biy, yl):
    with self.fig:
      self.fig.clf()
      self.fig.gca().plot(x, y, ls="solid", label=r"$\nu_\mu$ NH")
      self.fig.gca().plot(x, by, ls="solid", label=r"$\bar{\nu}$ NH")
      self.fig.gca().plot(x, iy, ls="dashed", label=r"$\nu$ IH")
      self.fig.gca().plot(x, biy, ls="dashed", label=r"$\bar{\nu}$ IH")
      self.fig.legend()
      self.fig.gca().set_ylim([0,self.maxy])
      self.fig.gca().set_ylabel(yl)
      self.fig.gca().set_xlabel("Enu")

with ui.row():
  musurv = oscprob(1)
  eapp = oscprob(0.2)

last = [-10,-10,-10]

def update_data_elements(vals):
  start = datetime.datetime.now()
  global last

  # changed = False
  # for i in range(len(vals)):
  #   if abs(last[i] - vals[i]) > 5:
  #     changed = True
  #     break

  # if not changed:
  #   return
  # last = vals

  tbl_update(vals)
  for v in valtraces:
    v.update(vals)

  print("param update took %s ms" % (datetime.datetime.now() - start).microseconds)
  start = datetime.datetime.now()

  physv = [converters[i](x) for i,x in enumerate(vals)]
  print(physv)

  L = 1300 # km
  rho = 3 # g/cc
  Ye = 0.5
  N_Newton = 0
  s12sq = 0.31
  s13sq = 0.02
  s23sq = physv[1]
  delta = physv[2] * np.pi
  Dmsq21 = 7.5e-5 # eV^2
  Dmsq31 = (physv[0] * 1E-3) + Dmsq21 # eV^2
  iDmsq31 = (-physv[0] * 1E-3) + Dmsq21 # eV^2

  enur = np.logspace(-0.3,0.7,50)


  oprobs = [Probability_Matter_LBL(s12sq, s13sq, s23sq, delta, Dmsq21, Dmsq31, L, x, rho, Ye, N_Newton) for x in enur]
  boprobs = [Probability_Matter_LBL(s12sq, s13sq, s23sq, delta, Dmsq21, Dmsq31, L, -x, rho, Ye, N_Newton) for x in enur]
  ioprobs = [Probability_Matter_LBL(s12sq, s13sq, s23sq, delta, Dmsq21, iDmsq31, L, x, rho, Ye, N_Newton) for x in enur]
  bioprobs = [Probability_Matter_LBL(s12sq, s13sq, s23sq, delta, Dmsq21, iDmsq31, L, -x, rho, Ye, N_Newton) for x in enur]

  print("osc prob calc took %s ms" % (datetime.datetime.now() - start).microseconds)
  start = datetime.datetime.now()

  musurv.update(enur, [x[1][1] for x in oprobs],
                      [x[1][1] for x in boprobs],
                      [x[1][1] for x in ioprobs],
                      [x[1][1] for x in bioprobs],
                      r"$P_{\nu_{\mu}\rightarrow\nu_{\mu}}$")
  eapp.update(enur, [x[1][0] for x in oprobs],
                    [x[1][0] for x in boprobs],
                    [x[1][0] for x in ioprobs],
                    [x[1][0] for x in bioprobs],
                    r"$P_{\nu_{\mu}\rightarrow\nu_{e}}$")
  print("osc prob plot update took %s ms" % (datetime.datetime.now() - start).microseconds)

new_vals_available.subscribe(update_data_elements)

ui.run()
