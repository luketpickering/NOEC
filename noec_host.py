#! /usr/bin/env python3

import serial
import vals_pb2
import types
import sys

from multiprocessing import Process, Queue

def unescape_msg(bytstr):
  obs = b''
  i = 0
  while i < len(bytstr):
    if bytstr[i] == 0xe0:
      i += 1
      if bytstr[i] == 0xe0:
        obs += b'\xe0'
      elif bytstr[i] == 0xe1:
        obs += b'\xf1'
      elif bytstr[i] == 0xe2:
        obs += b'\xf2'
      elif bytstr[i] == 0xe3:
        obs += b'\xf3'
      else:
        raise RuntimeError("Encountered badly escaped message: %s" % ''.join(format(x, '02x') for x in bytstr))
    else:
      obs += bytes([bytstr[i]])
    i += 1
  return obs

def monitor_serial(resultq, port, fmt="raw3x16", baud=9600, timeout=None, num_vals=3):
  msg = types.SimpleNamespace()

  msg.cmd = vals_pb2.Command()
  msg.upbody = vals_pb2.UpdateBody()

  values = {x: 0 for x in range(num_vals)}

  if fmt == "raw3x16":
    with serial.Serial(port, baud, timeout=timeout) as ser:
      while True:
        ser.read_until(b'\xf1') #message magic byte

        cmdmsg = ser.read_until(b'\xf2')
        print(f"recieved cmd[{len(cmdmsg)}]: %s" % ''.join(format(x, '02x') for x in cmdmsg))
        esc_cmdmsg = unescape_msg(cmdmsg[:-1])
        print(f"    escaped to [{len(esc_cmdmsg)}]: %s" % ''.join(format(x, '02x') for x in esc_cmdmsg))
        cmd = esc_cmdmsg[0]
        print(f"-- CMD: {cmd} --")

        bodymsg = ser.read_until(b'\xf3')
        print(f"recieved update body[{len(bodymsg)}]: %s" % ''.join(format(x, '02x') for x in bodymsg))
        esc_bodymsg = unescape_msg(bodymsg[:-1])
        print(f"    escaped to [{len(esc_bodymsg)}]: %s" % ''.join(format(x, '02x') for x in esc_bodymsg))
        u16s = []
        for i in range(0,len(esc_bodymsg),2):
          u16 = (int(esc_bodymsg[i]) << 8) + int(esc_bodymsg[i+1])
          u16s.append(u16)


        tick = u16s[0]
        print(f"-- TICK: {tick} -- {u16s[1:]}")
        resultq.put([x >> 8 for x in u16s[1:]])

  elif fmt == "protobuf":
    with serial.Serial(port, baud, timeout=timeout) as ser:
      while True:
        ser.read_until(b'\xf1') #message magic byte

        cmdmsg = ser.read_until(b'\xf2')
        print(f"recieved cmd[{len(cmdmsg)}]: %s" % ''.join(format(x, '02x') for x in cmdmsg))
        esc_cmdmsg = unescape_msg(cmdmsg[:-1])
        print(f"    escaped to [{len(esc_cmdmsg)}]: %s" % ''.join(format(x, '02x') for x in esc_cmdmsg))
        msg.cmd.ParseFromString(esc_cmdmsg)

        bodymsg = ser.read_until(b'\xf3')
        print(f"recieved update body[{len(bodymsg)}]: %s" % ''.join(format(x, '02x') for x in bodymsg))
        esc_bodymsg = unescape_msg(bodymsg[:-1])
        print(f"    escaped to [{len(esc_bodymsg)}]: %s" % ''.join(format(x, '02x') for x in esc_bodymsg))
        msg.upbody.ParseFromString(esc_bodymsg)

        updated = False
        for i in msg.upbody.values.keys():
          if i in values:
            values[i] = msg.upbody.values[i]
            print(f"[MNTR]: Found update for value {i} = {values[i]}")
            updated = True

        if updated:
          resultq.put(values)
  else:
    raise RuntimeError(f"invalid serial format: {fmt}")

if __name__ == '__main__':

  resultq = Queue()
  monitorproc = Process(target=monitor_serial, args=(resultq, sys.argv[1]))
  monitorproc.start()

  while True:
    try:
      print(f"[MAIN] Updated values: {resultq.get(block=True, timeout=2)}")
    except Exception:
      monitorproc.kill()
      break
