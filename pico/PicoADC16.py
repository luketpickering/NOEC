from machine import Pin, SPI

class PicoADC16:
  def __init__(self, SPIBank=0, baudrate=1_000_000, polarity=0, phase=0,
                     sck=2, mosi=3, miso=4, cs_pins=[1,5]):

    self.spi = SPI(SPIBank, baudrate=baudrate, polarity=polarity,
                           phase=phase, sck=sck, mosi=mosi, miso=miso)
    self.chip_select = [ Pin(p, mode=Pin.OUT, value=1) for p in cs_pins ]

    self.buf_in = bytearray(3)
    self.buf_in[0] = 0x1
    self.buf_out = bytearray(3)

  def _readadc(self, chan):
    cs = self.chip_select[chan // 8]
    bank_chan = (chan % 8)

    self.buf_in[1] = (0x1 << 7) | (bank_chan << 4)

    cs(0)
    spi_adc.write_readinto(self.buf_in, self.buf_out)
    cs(1)

    return int( ((self.buf_out[1] & 0x03) << 8 ) | self.buf_out[2])

  def readadc_u10(channels, samples=200):
    vals = [self._readadc(c) for c in channels]
    for i in range(samples-1):
      for j,v in enumerate([self._readadc(c) for c in channels]):
        vals[j] += v

    return [v/200.0 for v in vals]
