#!/usr/bin/env python2.7
'''Docstring

'''
# Copyleft by Pawel Chojnacki

__author__ = 'Pawel "duskglow" Chojnacki'
__copyright__ = 'Copyleft 2013 Pawel Chojnacki'
__version__ = '0.0.3'
__date__ = '14.05.2013'
__license__ = 'GPLv3'

import argparse as ap
import Image as im  # Image manipulation
import numpy as np
#~ import sys # Is it really needed?


class Overlord(object):
    '''Class Overlord
    Responsible for interacting with user and creating objects using other 
    classes.
    '''

    def __init__(self):

        '''Parsing arguments'''
        options = ap.ArgumentParser(
            prog="stegnograPy",
            description="A simple python program used to hide text inside \
            pictures. Supported formats are")
        options.add_argument("image", help="path to image")
        mode = options.add_mutually_exclusive_group(required=True)
        mode.add_argument(
            "-I", "--info", action="store_true",
            help="show information about image")
        mode.add_argument(
            "-R", "--read", action="store_true",
            help="decode text from image")
        mode.add_argument(
            "-W", "--write", type=str,
            help="encode text into image")
        # TEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEST
        mode.add_argument(
            "-t", "--test", action="store_true")
        encoding = options.add_mutually_exclusive_group()
        encoding.add_argument(
            "-u", "--vulgar", action="store_true",
            help="vulgar encoding algorithm")
        encoding.add_argument(
            "-s", "--subtle", action="store_true",
            help="subtle encoding algorithm")
        options.add_argument(
            "-k", "--key",
            help="key used to choose encoded pixels")
        volume = options.add_mutually_exclusive_group()
        volume.add_argument(
            "-v",  "--verbose", action="store_true",
            default=0,  help="verbose mode: print it all!")
        volume.add_argument(
            "-q",  "--quiet", action="store_true",
            default=0,  help="quiet mode: shhhh!")
        args = options.parse_args()

        print args

        if args.info:
            km = Keymaster('info')
        elif args.read:
            km = Keyaster('read', key=args.key)
        elif args.write:
            pass
            #~ km = Keymaster('write', key=args.key)
            #~ km.write(text)
        if args.quiet:
            # global quiet
            quiet = True
        elif args.verbose:
            # global verbose
            verbose = True

        # Sprawdzic,  czy args.image jest obrazkiem
        img = Painter(args.image)
        print img.test_subtle((224, 6322, 8537, 7437))
    # CASE SENSITIVE FILENAMES


class Keymaster(object):
    '''Holds teh keys'''

    def __init__(self, mode, text=0, key=0):
        pass

    # Manager and keymaster


class Painter(object):
    '''Class Painter
    Responsible for dealing with the image itself.
    '''

    def __init__(self, filename):
        # sprawdzenie,  czy obrazek istnieje -> do kontrolera
        # sprawdzenie,  czy jest obrazem
        self.img = im.open(filename)
        self.format = self.img.format
        self.size = self.img.size
        self.mode = self.img.mode
        self.key = []

    def set_key(self, key):
        '''Generates a matrix of x,y pixel coordinates from numeric key'''
        for i in len(key):
            self.key.append((key[i] / self.size[0], key[i] % self.size[0]))

    def test_vulgar(self, key):
        '''Tests if given key can be used for vulgar encoding.'''
        return max(key) > self.size[0]*self.size[1]

    def test_subtle(self, key):
        '''Tests if given key can be used for subtle encoding.
        Consists of three parts: vulgar, rimming and vicinity tests.
        '''
        if self.test_vulgar(key):
            return 1
        coordinates = []
        for i in range(len(key)):
            coo_x = key[i] % self.size[0]
            coo_y = key[i] / self.size[0]
            if coo_x in [0, self.size[0]-1] or coo_y in [0, self.size[0]-1]:
                return 1
            coordinates.append((coo_y, coo_x))
        for i in range(len(coordinates)):
            coo_x = coordinates[i][1]
            coo_y = coordinates[i][0]
            copy = np.array(coordinates[:i]+coordinates[i+1:])
            vicinity_x = np.array(())
            vicinity_y = np.array(())
            for j in (coo_x-1, coo_x, coo_x+1):
                vicinity_x = np.append(vicinity_x, np.where(copy[:, -1] == j))
            for j in (coo_y-1, coo_y, coo_y+1):
                vicinity_y = np.append(vicinity_y, np.where(copy[:, 0] == j))
            if bool(set(vicinity_x) & set(vicinity_y)):
                return 1
        return 0

    @property
    def info(self):
        '''Public method of showing information about an image'''
        return self.format, self.size, self.mode, self.key

    def preview(self, key):
        ''' docstring '''
        # key to lista pikseli obliczona w keymasterze
        # chodzi o podglad graficzny z pikselami w innym kolorze
        pass

    def read_vulgar(self):
        '''Reads the pixels by key'''
        key = self.key
        pixels = []
        for i in len(key):
            pixels.append(self.img.getpixel(key[i]))
        return pixels

    def read_subtle(self):
        '''Reads the pixels and their vicinity by key'''   
        key = self.key     
        pixels = []
        for i in len(key):
            coo_x = key[i][1]
            coo_y = key[i][0]
            vincinity = [
                [coo_y-1, coo_x-1], [coo_y-1, coo_x], [coo_y-1, coo_x+1],
                 [coo_y, coo_x-1],   [coo_y, coo_x],   [coo_y, coo_x+1],
                [coo_y+1, coo_x-1], [coo_y+1, coo_x], [coo_y+1, coo_x+1]
                ]
            pixels[i] = []
            for j in vincinity:
                pixels[i].append(self.img.getpixel(j))

    def save_pixel(self, place, color):
        '''Saves one pixel of a given color at the given location.'''
        self.img.putpixel(place, color)

    # def save_subtle(self, place, color):
    #     '''Saves one pixel of a given color by difference from others'''
    #     coo_x = place[1]
    #     coo_y = place[0]
    #     vincinity = [
    #         [coo_y-1, coo_x-1], [coo_y-1, coo_x], [coo_y-1, coo_x+1],
    #          [coo_y, coo_x-1],   [coo_y, coo_x],   [coo_y, coo_x+1],
    #         [coo_y+1, coo_x-1], [coo_y+1, coo_x], [coo_y+1, coo_x+1]
    #         ]

class Encode(object):
    pass


class Vulgar(Encode):
    pass


class Subtle(Encode):
    pass

if __name__ == '__main__':
    Overlord()
