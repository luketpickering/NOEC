from text import characters
from machine import UART,Pin, I2C, SPI
from time import sleep
from neopixel import NeoPixel
neopin = Pin(16, Pin.OUT, value=0)
sleep(0.001)  # reset WS2812B
neo = NeoPixel(neopin, 160, bpp=3, timing=(300,800,800,300))

def create_text_array(string):
    text_array = [[0 for i in range(len(string)*6 + 2*16)] for i in range(10)]
    for i in range(len(string)):
        current_char = characters[string[i]]
        for j in range(10):
            text_array[j][16+i*6:16+i*6+5] = current_char[j]
        
    return text_array
    
def get_text_subsection(text_array, starting_pos):
    section = []
    for i in range(10):
        for j in range(16):
            section.append(text_array[i][j + starting_pos])
    return section

def write_subsection(text_section, colour, neopixel):
    for i in range(160):
        j = text_section[i]
        neopixel[i] = (j*colour[0],j*colour[1],j*colour[2])
    neopixel.write()

def scroll_text(neopixel,string, colour, scroll_wait =0.1):
    text = create_text_array(string)
    for i in range(len(text[0])-16):
        section = get_text_subsection(text,i)
        write_subsection(section, colour,neopixel)
        sleep(scroll_wait)
    
text = create_text_array("DUNE")
section = get_text_subsection(text,0)
colour = (32,0,0)
write_subsection(section, colour, neo)
while True:
    scroll_text(neo,"DUNEDUNEDUNEDUNE",colour)
