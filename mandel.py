from PIL import Image
from complex_even_fraction import ComplexEvenFraction
from complex_even_fraction import EvenFraction
import colorsys
import sys
import logging

logging.basicConfig(level=logging.INFO)

def get_iternum(z, c, bailout):
    i = 0
    while (z.in4()) and (i < bailout):
        logging.info("iteration: %i", i)
        z = z * z + c
        i += 1
    return i

def draw_mandelbrot(left, top, scale_log, bitmap_width_log, bitmap_height_log, bailout):
    field = [] * (1 << bitmap_height_log)
    for x in range(1 << bitmap_height_log):
        field.append([0] * (1 << bitmap_width_log))
    
    for i in range(1 << bitmap_height_log):
        for j in range(1 << bitmap_width_log):
            x = left + EvenFraction(j, bitmap_width_log + scale_log)
            y = top - EvenFraction(i, bitmap_height_log + scale_log)
            c = ComplexEvenFraction(x, y)
            z = ComplexEvenFraction()
            logging.info("getting iternum of [%i, %i]", i, j)
            field[i][j] = get_iternum(z, c, bailout)        
            logging.info("done")
    return field


def color(c):
    h = (c % 6) / 6
    s = 1
    v = 255
    r, g, b = colorsys.hsv_to_rgb(h, s, v)
    r, g, b = map(int, [r, g, b])
    return r + g * 0x100 + b * 0x10000
    
    
def get_zoom_params(tile_x, tile_y, zoom):
    LEFT = -2
    TOP = 2
    left = EvenFraction(LEFT, 0) + EvenFraction(tile_x << 2, zoom)
    top = EvenFraction(TOP, 0) - EvenFraction(tile_y << 2, zoom)
    return left, top, zoom - 2
    

def quadkey_to_xyz(quadkey):
    zoom = len(quadkey)
    x = 0
    y = 0
    for c in quadkey:
        x <<= 1
        y <<= 1
        level = int(c)
        x |= (level & 1)
        y |= ((level >> 1) & 1)
    return x, y, zoom
    
def make_tile(quadkey, bailout):
    TILE_WIDTH_LOG = 8
    TILE_HEIGHT_LOG = 8
    tile_x, tile_y, zoom = quadkey_to_xyz(quadkey)
    print(tile_x, tile_y, zoom)
    left, top, scale_log = get_zoom_params(tile_x, tile_y, zoom)
    im = Image.new("RGB", (1 << TILE_WIDTH_LOG, 1 << TILE_HEIGHT_LOG))
    for y, row in enumerate(draw_mandelbrot(left, top, scale_log, TILE_WIDTH_LOG, TILE_HEIGHT_LOG, bailout)):
        for x, c in enumerate(row):
            im.putpixel((x, y), color(c))
    im.save("%s_%s_%s.png" % (tile_y, tile_x, zoom))

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: m.py quadkey bailout")
    quadkey = sys.argv[1]
    bailout = int(sys.argv[2])
    make_tile(quadkey, bailout)
