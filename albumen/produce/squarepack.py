import fractions
import math
import random
import sys
import os

import Image

from pprint import pprint

import analysis_cache

def random_iterate(src):
    new_src = list(src)
    for _ in range(len(new_src)):
        x = random.choice(new_src)
        yield x
        new_src.remove(x)

class ImageGrid(object):
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.size = self.x * self.y
        self.data = {}
        for i in range(self.x):
            for j in range(self.y):
                self.data[(i,j)] = [1, ''] 

    def join(self, i, j):
        self.data[(i,j)][0] += 1
        del self.data[(i+1, j)]
        del self.data[(i, j+1)]
        del self.data[(i+1, j+1)]
        self.size -= 3

    def unjoin(self, i, j):
        if (i, j) not in self.data or self.data[(i,j)][0] == 1:
            return
        self.data[(i,j)][0] -= 1
        self.data[(i+1, j)] = [1, '']
        self.data[(i, j+1)] = [1, '']
        self.data[(i+1, j+1)] = [1, '']
        self.size += 3

    def possible_joins(self):
        candidates = []
        for i in range(self.x - 1):
            for j in range(self.y - 1):
                if self._can_join(i,j):
                    candidates.append((i,j))
        return candidates

    def _can_join(self, i, j):
        for coords in ((i,j), (i+1,j), (i,j+1), (i+1,j+1)):
            if coords not in self.data:
                return False
            if self.data[coords][0] != 1:
                return False
        return True       

def gen_grid(x, y, n):
    """
        x - max number of cells horizontally
        y - max number of cells vertically
        n - number of images to fit (if n >= x*y, return x*y)
    """
    g = ImageGrid(x, y)
    if not grid_reduce(g, n):
        return None
    return g    

def grid_reduce(g, n):
    if g.size <= n:
        return True
    candidates = g.possible_joins()
    if not candidates:
        return False
    for coord in random_iterate(candidates):
        g.join(*coord)
        if grid_reduce(g, n):
            return True
        else:  
            g.unjoin(*coord)
    return False

def gen_image(g, attr, cell=100):
    img = Image.new('RGBA', (cell*g.x, cell*g.y))
    sources = [x.meta['filename'] for x in analysis_cache.get_images(sort_field=attr)]
    for coord, spec in g.data.iteritems():
        src = sources.pop(0)
        print coord, spec[0], src
        src_img = Image.open('samples/%s' % src).resize((cell*spec[0], cell*spec[0]), Image.ANTIALIAS)
        box = (cell*coord[0], cell*coord[1], cell*(coord[0] + spec[0]), cell*(coord[1] + spec[0]))
        img.paste(src_img, box)
    return img

def gen_spec(xpx, ypx, n):
    """
        in: xpx, ypx, n
        out: xcells, ycells, cellsize
    """ 
    gcd = fractions.gcd(xpx, ypx)
    min_xcells = xpx/gcd
    min_ycells = ypx/gcd
    scale = int(math.ceil(float(n)/(min_xcells*min_ycells)))
    return scale*min_xcells, scale*min_ycells, xpx/(scale*min_xcells)

def main(x,y,n, attr):
    xcell, ycell, cellsize = gen_spec(x, y, n)
    g = gen_grid(xcell, ycell, n)
    im = gen_image(g, attr=attr, cell=cellsize)
    im.save('bg_%s.png' % attr, format='PNG')
    im.show()

if __name__ == '__main__':
    main(int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3]), sys.argv[4])