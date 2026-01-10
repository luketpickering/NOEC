#!/usr/bin/env python3

import json
import asyncio
import sys

from websockets.asyncio.server import serve

from noec_host import NOECHost

def process(vals):
  return {"values": vals}

async def forward_to_ws(serial_device, baud, websocket):
  host = NOECHost(serial_device, baud)
  while True:
    data_from_device = await host.read()
    data_to_ui = process(data_from_device)
    await websocket.send(json.dumps(data_to_ui))

async def NOECWSServer(serial_device, baud=9600, ws_port=5678):
  async with serve(lambda ws: forward_to_ws(serial_device, baud, ws), "localhost", ws_port) as server:
    await server.serve_forever()

if __name__ == "__main__":
  asyncio.run(NOECWSServer(sys.argv[1]))
