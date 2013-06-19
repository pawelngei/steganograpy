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
    '''Manages the flow of the program. CLI and commands.'''

    def __init__(self):
        self.options = 0
        self.mode = 0
        self.encoding = 0
        self.volume = 0
        self.args = 0

    def parser(self):
        '''Parses the CLI's arguments.'''
        self.options = ap.ArgumentParser(
            prog="stegnograPy",
            description="A simple python program used to hide text inside \
            pictures. Supported formats are")
        self.options.add_argument("image", help="path to image")
        self.mode = self.options.add_mutually_exclusive_group(required=True)
        self.mode.add_argument(
            "-I", "--info", action="store_true",
            help="show information about image")
        self.mode.add_argument(
            "-R", "--read", action="store_true",
            help="decode text from image")
        self.mode.add_argument(
            "-W", "--write", type=str,
            help="encode text into image")
        self.mode.add_argument(
            "-p", "--preview", action="store_true")
        self.encoding = self.options.add_mutually_exclusive_group()
        self.encoding.add_argument(
            "-u", "--vulgar", action="store_true",
            help="vulgar encoding algorithm")
        self.encoding.add_argument(
            "-s", "--subtle", action="store_true",
            help="subtle encoding algorithm")
        self.options.add_argument(
            "-k", "--key",
            help="key used to choose encoded pixels")
        self.options.add_argument(
            "-o", "--output",
            help="output filename and location")
        self.volume = self.options.add_mutually_exclusive_group()
        self.volume.add_argument(
            "-v",  "--verbose", action="store_true",
            default=0,  help="verbose mode: print it all!")
        self.volume.add_argument(
            "-q",  "--quiet", action="store_true",
            default=0,  help="quiet mode: shhhh!")
        self.args = self.options.parse_args()

class Keymaster(object):
    '''Holds teh keys'''

    def __init__(self, mode, text=0, key=0):
        self.mode = mode
        self.text = text
        self.key = key
        # self.dict = {
            # 'cotrzeci' 
        # }
        # NO LONGER THAN THE IMAGE! REMEMBER
    # Manager and keymaster
    # Library od lambda? To decide.

    
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
        self.length = self.size[0]*self.size[1]
        self.mode = self.img.mode
        self.key = []

    def set_key(self, key):
        '''Generates a matrix of x,y pixel coordinates from numeric key'''
        for i in key:
            self.key.append((i / self.size[0], i % self.size[0]))

    def test_vulgar(self, key):
        '''Tests if given key can be used for vulgar encoding.'''
        if max(key) > self.length:
            return True
        elif len(key) > self.length:
            return True
        else:
            return False

    def test_subtle(self, key):
        '''Tests if given key can be used for subtle encoding.
        Consists of three parts: vulgar, rimming and vicinity tests.
        '''
        if self.test_vulgar(key):
            return True
        coordinates = []
        for i in range(len(key)):
            coo_x = key[i] % self.size[0]
            coo_y = key[i] / self.size[0]
            if coo_x in [0, self.size[0]-1] or coo_y in [0, self.size[0]-1]:
                return True
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
                return True
        return 0

    @property
    def info(self):
        '''Public method of showing information about an image.'''
        return self.format, self.size, self.mode, self.key

    def preview(self):
        '''Shows preview of the key in the image.'''
        prvv = self
        for i in self.key:
            prvv.save_pixel(i, (255, 0, 230))
        prvv.img.show()

    def read_vulgar(self):
        '''Reads the pixels by key'''
        key = self.key
        pixels = []
        for i in len(key):
            pixels.append(self.img.getpixel(key[i]))
        return pixels

    def read_subtle(self):
        '''Reads the pixels and their vicinity by key.'''   
        key = self.key     
        pixels = np.empty(len(self.key))
        for i in range(len(key)):
            x = key[i][1]
            y = key[i][0]
            vinc_idx = np.array(
                np.array(y-1, x-1), np.array(y-1, x), np.array(y-1, x+1),
                np.array([y, x-1]),                    np.array(y, x+1),
                np.array(y+1, x-1), np.array(y+1, x), np.array(y+1, x+1)
                )
            vincinity = np.array()
            for j in vinc_idx:
                np.append(vincinity[i], self.img.getpixel(j))
                # There is virtually NO POINT in returning the whole list,
                # when we're interested only in the middle point and the
                # mean of the orhers, is it?
            channels = np.empty(3)
            for k in range(3):
                channels[k] = np.mean(vincinity[:, k])
            pixels[i] = np.array(channels, self.img.getpixel(x, y))
        return pixels
        # Structure of pixels as follows
        # [[[meanCH1,meanCH2,meanCH3],[xyCH1,xyCH2,xyCH3]],...]

    def save_pixel(self, place, color):
        '''Saves one pixel of a given color at the given location.'''
        self.img.putpixel(place, color)

    def save(self, location):
        '''Saves the modified file at the given location.'''
        self.img.save(location)


class Coder(object):
    '''Encodes and decodes text into pixels.'''

    def __init__(self, painting):
        self.painting = painting
        self.rawtext = []
        self.rawpix = []

    def test_encode(self, text, key):
        '''Tests if a text of a given length can be encoded.
        Returns True if text too long.'''
        if len(text) > len(key):
            return True
        elif not isinstance(text, str):
            return True

class VulgarCoder(Coder):
    '''Encodes and decodes using vulgar methods.'''

    def encode(self, text):
        '''Encodes text into pixels using vulgar methods.'''
        self.rawtext = list(text)
        channels = []
        for i in self.rawtext:
            # Adding 63 to average the vulgarity
            channels.append(ord(i)+63)
        if channels % 3 != 0:
            channels.append([0]*(channels%3))
        for i in range(0, len(channels), 3):
            single_px = []
            for j in range(3):
                single_px.append(channels[i+j])
            self.rawpix.append(single_px)
            place = self.painting.key[i/3]
            self.painting.save_pixel(place, single_px)

    def decode(self):
        '''Decodes pixels to text using vulgar methods.'''
        pixels = self.painting.read_vulgar()
        for i in pixels:
            for j in i:
                self.rawpix.append(j)
        for i in self.rawpix:
            # Substracting 63 to average the vulgarity
            self.rawtext.append(chr(i-63))
        return str(self.rawtext)

class SubtleCoder(Coder):
    '''Encodes and decodes using subtle methods.'''

    def encode(self, text):
        '''Enodes text into pixels using subtle methods.'''
        self.rawtext = list(text)
        channels = []
        for i in self.rawtext:
            channels.append(ord(i))
        if channels % 3 != 0:
            channels.append([0]*(channels%3))
        neighbourhoods = self.painting.read_subtle()
        for i in range(0, len(channels), 3):
            single_px = []
            for j in range(3):
                vicinity = neighbourhoods[i/3, 0, j]
                if vicinity <= 127:
                    single_px.append(vicinity+channels[i+j])
                else:
                    single_px.append(vicinity-channels[i+j])
            self.rawpix.append(single_px)
            place = self.painting.key[i/3]
            self.painting.save_pixel(place, single_px)

    def decode(self):
        '''Decodes pixels to text using subtle methods.'''
        neighbourhoods = self.painting.read_subtle()[:, 0]
        self.rawpix = self.painting.read_subtle()[:, 1]
        for i in range(len(self.rawpix)):
            vicinity = neighbourhoods[i]
            if vicinity <= 127:
                channel = chr(self.rawpix[i]-vicinity)
            else:
                channel = chr(vicinity-self.rawpix[i])
            self.rawtext.append(channel)
        return str(self.rawtext)

if __name__ == '__main__':
    OVERLORD = Overlord()
    OVERLORD.parser()

    print OVERLORD.args

    if OVERLORD.args.info:
        km = Keymaster(0)

    elif OVERLORD.args.read:
        km = Keyaster(1, key=OVERLORD.args.key)
    elif OVERLORD.args.write:
        km = Keymaster(2, key=OVERLORD.args.key)
        km.write(text)
    if OVERLORD.args.quiet:
        # global quiet
        quiet = True
    elif OVERLORD.args.verbose:
        # global verbose
        verbose = True

    # Sprawdzic,  czy args.image jest obrazkiem
    img = Painter(args.image)
    # print img.test_subtle((224, 6322, 8537, 7437))
    print img.test_subtle(np.arange(101,9899,10))
    img.set_key(np.arange(101,9899,13))
    img.preview()

# CASE SENSITIVE FILENAMES
