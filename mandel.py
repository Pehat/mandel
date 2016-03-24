from PIL import Image
from complex_even_fraction import ComplexEvenFraction
from complex_even_fraction import EvenFraction
import colorsys
import sys
import logging
import pickle
import os
import multiprocessing
import datetime

TILE_WIDTH_LOG = 8
TILE_HEIGHT_LOG = 8
ROOT_DIR = "tiles"
DIRNAME_LEN = 4
ASCII_ART = '.,"+*#'

def get_iternum(item):
    i, j, z, c, bailout = item
    iter_count = 0
    while (z.in4()) and (iter_count < bailout):
        z = z * z + c
        iter_count += 1
    return i, j, iter_count


def draw_mandelbrot(left, top, scale_log, bitmap_width_log, bitmap_height_log, bailout):
    field = [] * (1 << bitmap_height_log)
    for x in range(1 << bitmap_height_log):
        field.append([None] * (1 << bitmap_width_log))

    tasks = []
    pool = multiprocessing.Pool(4)
    for i in range(1 << bitmap_height_log):
        for j in range(1 << bitmap_width_log):
            x = left + EvenFraction(j, bitmap_width_log + scale_log)
            y = top - EvenFraction(i, bitmap_height_log + scale_log)
            c = ComplexEvenFraction(x, y)
            z = ComplexEvenFraction()
            tasks.append((i, j, z, c, bailout))
    
    wait_x, wait_y = (0, 0)
    step_x = 4
    step_y = 8
    
    for i, j, iter_count in pool.imap_unordered(get_iternum, tasks):
        field[i][j] = iter_count
        while (wait_y != (1 << bitmap_height_log)) and (field[wait_y][wait_x] is not None):
            iter_count = field[wait_y][wait_x]
            print(ASCII_ART[iter_count % len(ASCII_ART)], end='')
            sys.stdout.flush()
            wait_x += step_x
            if wait_x == 1 << bitmap_width_log:
                print()
                wait_x = 0
                wait_y += step_y
    pool.close()
    pool.join()
    pool.terminate()
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


def get_quad_path(quadkey):
    return os.path.join(ROOT_DIR, *[quadkey[i: i + DIRNAME_LEN] for i in range(0, len(quadkey), DIRNAME_LEN)])


def get_png_path(quadkey):
    return get_quad_path(quadkey) + ".png"


def get_bin_path(quadkey):
    return get_quad_path(quadkey) + ".bin"


def ensure_path(quadkey):
    os.makedirs(os.path.dirname(get_quad_path(quadkey)) or '.', exist_ok=True)


def save_image(quadkey, im):
    ensure_path(quadkey)
    im.save(get_png_path(quadkey))


def save_bin(quadkey, field):
    ensure_path(quadkey)
    with open(get_bin_path(quadkey), 'wb') as output_file:
        pickle.dump([quadkey, field], output_file)


def render_field(quadkey, field):
    im = Image.new("RGB", (1 << TILE_WIDTH_LOG, 1 << TILE_HEIGHT_LOG))
    for y, row in enumerate(field):
        for x, c in enumerate(row):
            im.putpixel((x, y), color(c))
    save_image(quadkey, im)
    
    
def make_tile(quadkey, bailout):
    tile_x, tile_y, zoom = quadkey_to_xyz(quadkey)
    print(tile_x, tile_y, zoom)
    left, top, scale_log = get_zoom_params(tile_x, tile_y, zoom)
    field = draw_mandelbrot(left, top, scale_log, TILE_WIDTH_LOG, TILE_HEIGHT_LOG, bailout)
    save_bin(quadkey, field)
    render_field(quadkey, field)

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: m.py quadkey bailout")
    quadkey = sys.argv[1]
    bailout = int(sys.argv[2])
    make_tile(quadkey, bailout)
