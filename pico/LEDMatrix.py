from neopixel import NeoPixel
from time import sleep

class LEDMatrixLevels():
  def __init__(self, pin):
    self.neopin = Pin(pin, Pin.OUT, value=0)
    sleep(0.001)
    self.np = NeoPixel(self.neopin, 160, bpp=3, timing=(300,800,800,300))

  def _setxy(self, x, y, rgb):
    self.np[x + y*16] = rgb

  def _write(self):
    self.np.write()

  def _setrowlevel(self, row, level_u5, rgb):
    for i in range(16):
      if level_u5 > i:
        self._setxy(i, row, rgb)

  def setlevel_u10(self, row, level_u10, rgb):
    self.setrowlevel(row, int(level_u10 * (16/1024)), rgb)
    self._write()

  def setlevels_u10(self, levels_u10, rgbs):
    for i,l in enumerate(levels_u5):
      self.setrowlevel(i, int(l * (16/1024)), rgbs[i])
    self._write()
