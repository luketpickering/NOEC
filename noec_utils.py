import json

def noec_escape_bytstr(bytstr):
  obs = bytearray()
  for c in bytstr:
    if c == 0xf1:
      obs += b'\xe0\xe1'
    elif c == 0xf2:
      obs += b'\xe0\xe2'
    elif c == 0xe0:
      obs += b'\xe0\xe0'
    else:
      obs += bytes([c])
  return obs

def noec_unescape_bytstr(bytstr):
  obs = bytearray()
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
      else:
        raise RuntimeError("Encountered badly escaped message: %s" % ''.join(format(x, '02x') for x in bytstr))
    else:
      obs += bytes([bytstr[i]])
    i += 1
  return obs

def obj_to_msg(obj):
  return noec_escape_bytstr(json.dumps(obj).encode("utf-8"))

def msg_to_obj(msg):
  return json.loads(noec_unescape_bytstr(msg).decode("utf-8"))
