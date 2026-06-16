# NOEC

Neutrino Oscillation Experiment Control (outreach MCU project).

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

Find datasheets for the [pico](datasheets/RP-008304-DS-2-pico-2-w-datasheet.pdf),
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

## Host

The host computer recieves messages from the device, performs any neccessary
processing, and then sends messages to the front end via a websocket. The host
code is written in python and contained in the root directory of this
repository. The main programme is [noec_host.py](noec_host.py).

## Frontend
