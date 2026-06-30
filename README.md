# NOEC

Neutrino Oscillation Experiment Control (outreach MCU project).

## Quick Start

To start the [device emulator](#emulation), the [backend](#backend-on-host)
process, and the [frontend](#frontend) web server, you need 3 terminals:

```bash
#terminal 1 - front end web server
# pwd = /path/to/NOEC
cd d3frontend
python3 -m http.server
```

```bash
#terminal 2 - device emulator
# pwd = /path/to/NOEC
source venv/bin/activate
./noec_device_emulator.py
# this will start, tell you a device tty and wait for input
# you need to start the backend (noec_ws_server.py, below) passing
# this location and then return to this terminal and hit enter to connect
# up all the pipes. Example output below
#
# Client TTY name: /dev/ttys004
# Press Enter to start device emulator
```

```bash
#terminal 3 - device emulator
# pwd = /path/to/NOEC
source venv/bin/activate
# Run the below passing the tty device location shown in terminal 2, e.g.
./noec_ws_server.py /dev/ttys004
# now hit enter on terminal 2
```

If this all appears to work, then you can open a browser to `http://localhost:8000`.

## Device

Currently, the device is programmed in micropython. All micropython source can
be found within the [pico](pico/) directory. Communication with the device
currently uses the USB UART serial interface, though it would be possible to use
Bluetooth or WiFi instead. Development, source upload, and image flashing is
simplest in the officially supported [Thonny](https://thonny.org/) IDE.

### Documentation

The main web documentation for the Pico 2 can be found
[here](https://www.raspberrypi.com/documentation/microcontrollers/pico-series.html#pico2).

The wiki for MicroPython can be found
[here](https://github.com/micropython/micropython/wiki), though if you need to
flash a new image to the MCU you should use the images from RaspberryPi, found
[here](https://www.raspberrypi.com/documentation/microcontrollers/micropython.html#drag-and-drop-micropython).
**N.B.** The UF2 image that you need differs depending on if you are using a
board with WiFi or not.

Find datasheets for the [pico 2 (W)](datasheets/RP-008304-DS-2-pico-2-w-datasheet.pdf),
[MCP3008 ADC chip](datasheets/MCP3008.pdf),
[MCP23017 I/O Expander](datasheets/20001952c.pdf) and
[LED panel](datasheets/PicoRGBLED-Waveshare.pdf)
in [datasheets](datasheets/). The PicoADC16 hat doesn't have a datasheet *per
se*, but additional documentation can be found
[here](https://www.8086.net/product/picoadc16).

### Emulation

It may be easier to work on the host and frontend code without having the
physical device plugged in and running. There is a simple device emulator,
[noec_device_emulator.py](noec_device_emulator.py) that can be run on the host
and sends messages in the same format down a emulated serial device that the
host application can connect to as if it were the real device.

## Backend on Host

The host computer recieves messages from the device, performs any neccessary
processing, and then sends messages to the front end via a websocket. The host
code is written in python and contained in the root directory of this
repository. The main programme is [noec_host.py](noec_host.py).
There is a potentially useful [requirements.txt] file for creating a venv from.

## Frontend

The frontend is mostly written in Javascript, specifically using the
[d3.js](https://d3js.org/what-is-d3) library for visualisation via the SVG API.
The web page source can be found in [d3frontend](d3frontend/). For running on a
local machine, the builtin python webserver can be used like:

```bash
cd path/to/repo/d3frontend
python3 -m http.server
```

The frontend can then be accessed at [http://localhost:8000](http://localhost:8000).

## Physics

### Neutrino Oscillations Primer

There are many excellent resources for this, some are linked below:

* [Neutrino Oscillation Physics by Boris Kayser](https://arxiv.org/pdf/1206.4325)
* [Neutrino Oscillations by Steve Boyd](https://warwick.ac.uk/fac/sci/physics/staff/academic/boyd/stuff/neutrinolectures/lec_oscillations.pdf)
* [TASI Lectures on Neutrino Physics by André De Gouvêa](https://arxiv.org/pdf/hep-ph/0411274) Sections 3 & 4
* [Wikipedia](https://en.wikipedia.org/wiki/Neutrino_oscillation)

### Oscillation Probability Calculator

As the rest of our code is in python, we will use the open source
[nufast.py](nufast.py) to calculate oscillation probability where neccessary.
More details on the calculation and implementation of nufast can be found
[here](https://github.com/PeterDenton/NuFast-LBL/tree/v1.1) and
[here](https://arxiv.org/abs/2405.02400).

### Neutrino Interactions

### Detector Response

### Parametric Fitting

#### Histograms

#### Response functions

#### Goodness of Fit

#### Error Estimation

## Ideas For Where To Go Next

* Make the startup easier, should be able to start 1 script that spawns a
  webserver thread and takes an optional argument to spawn a emulator thread
  and open the pty pair, or take a serial device vfs location to recieve from
  the device.
* What might we want to try and 'teach' users?
  + Parametric inference or 'how we measure things in HEP' - Obvious links to ML/'AI'
    - Add automatic samplers that can run in parallel to inputs from the device. Could gamify finding the 'best' parameter values
    - Can demonstrate different sampling techniques: gradient descent, MCMC, many more complex options.
