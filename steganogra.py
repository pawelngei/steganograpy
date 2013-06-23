#!/usr/bin/env python2.7
'''Docstring

'''
# Copyleft by Pawel Chojnacki

__author__ = 'Pawel "duskglow" Chojnacki'
__copyright__ = 'Copyleft 2013 Pawel Chojnacki'
__version__ = '0.0.8.1'
__date__ = '24.06.2013'
__license__ = 'GPLv3'

import argparse as ap
import Image as im  # Image manipulation
import numpy as np
import random as r

class Overlord(object):
    '''Manages the flow of the program. CLI and commands.'''

    def __init__(self):
        '''Parses the CLI's arguments.'''
        options = ap.ArgumentParser(
            prog="stegnograPy",
            description="A simple python program used to hide text inside \
            pictures. Supported formats is PNG with RGB only.")
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
        mode.add_argument(
            "-p", "--preview", action="store_true")
        encoding = options.add_mutually_exclusive_group()
        encoding.add_argument(
            "-u", "--vulgar", action="store_true",
            help="vulgar encoding algorithm")
        encoding.add_argument(
            "-s", "--subtle", action="store_true",
            help="subtle encoding algorithm")
        keyring = options.add_mutually_exclusive_group()
        keyring.add_argument(
            "-k", "--key",
            help="preset key used to choose encoded pixels")
        keyring.add_argument(
            "-c", "--customkey",
            help="file storing a custom key to encode pixels",
            )
        options.add_argument(
            "-o", "--output",
            help="output filename and location")
        options.add_argument(
            "-v",  "--verbose", action="store_true",
            default=0,  help="verbose mode: print it all!")
        self.args = options.parse_args()

        self.vrb = self.args.verbose
        if self.vrb:
            print "Overlord: Verbose mode"
            print "Parsed arguments:", self.args

        self.painter = Painter(self.args.image)
        if self.vrb:
            print "Overlord: Testing picture"
        self.painter.test_picture()

        self.vlg = self.args.vulgar # T vulgar F subtle
        if self.vrb:
            print "Vulgar mode:", bool(self.vlg)
        if not self.vlg:
            if self.vrb:
                print "Overlord: testing if picture can be used with subtlety"
            self.painter.test_picture_subtle()

        self.key = Keymaster(self.vlg, self.painter.info, self.vrb)
        self.txt = self.args.write
        if self.vrb:
            print "Overlord: setting text to write to:", self.txt

        # INFO PART
        if self.args.info:
            if self.args.key or self.args.customkey:
                if self.vrb:
                    print "Overlord: entering info_key method."
                self.info_key()
            else:
                if self.vrb:
                    print "Overlord: entering info_image method."
                self.info_image()
        # READ PART
        if self.args.read:
            if self.vrb:
                print "Overlord: entering read method."
            self.read()
        # WRITE PART
        if self.args.write:
            self.path = self.args.output
            if self.vrb:
                print "Overlord: entering write method with path:", self.path
            self.write()

    def info_image(self):
        '''Provides information about the image.'''
        info = self.painter.info
        print("The picture size is:"), info[0][0], 'x', info[0][1]
        print("Stored in {!s} format using {!s} mode.".\
              format(info[1], info[2])) 
        print("Maximal vulgar key length is"), info[3]
        print("Maximal vulgar text length is"), info[3]*3
        print("Maximal subtle key length is"), info[4]
        print("Maximal subtle text length is"), info[4]*3

    def info_key(self):
        '''Provides information about the image and its key.'''
        info = self.painter.info
        print("The picture size is:"), info[0][0], 'x', info[0][1]
        print("Stored in {!s} format using {!s} mode.".\
              format(info[1], info[2])) 
        key = self.choose_keys()
        print("Choosen key maximum length is", len(key))
        print("Maximal text length written with it is", len(key)*3)
        print("Press P to preview or any other key to exit.")
        inp = raw_input()
        if inp in ['p','P']:
            self.painter.preview(self.painter.translate_matrix(key))
    
    def read(self):
        '''Controls other classes to read information from the image,\
        given key.
        '''
        if self.vrb:
            print "read: entering choose_keys method"
        key = self.choose_keys()
        if self.vrb:
            print("Using {!s} long key to read {!s} characters.".\
                            format(len(key),len(key)*3))
        if self.vlg:
            if self.vrb:
                print("Using vulgar encoding.")
            encoder = VulgarCoder()
        else:
            if self.vrb:
                print("Using subtle encoding.")
            encoder = SubtleCoder()
        matrix = self.painter.translate_matrix(key)
        if self.vrb:
            print "read: using painter.translate_matrix:", matrix
        text = encoder.decode(self.painter, matrix)
        if self.vrb:
            print("read: the encoded text is:")
        print text

    def write(self):
        '''Controls other classes to write information to the image with\
        appropriate key.
        '''
        text = self.txt
        key = self.choose_keys()
        if self.vrb:
            print "write: key chosen:", key
        endkey = self.mess_over(
            len(text),
            key)
        if self.vrb:
            print "write: messed with:", endkey
        matrix = self.painter.translate_matrix(endkey)
        if self.vrb:
            print "write: matrix translated:", matrix
        if self.vlg:
            coder = VulgarCoder()
            if self.vrb:
                print "write: VulgarCoder used"
        else:
            coder = SubtleCoder()
            if self.vrb:
                print "write: SubtleCoder used"
        if self.vrb:
            print "write: using coder.encode"
        coder.encode(
            text,
            self.painter,
            matrix)
        print("[P]review | [S]ave | [E]xit")
        inp = raw_input()
        if inp in ['p','P']:
            if self.vrb:
                print "write: using painter.postview"            
            self.painter.postview()
            print("[S]ave | [E]xit")
            cnf = raw_input()
            if cnf in ['s','S']:
                if self.vrb:
                    print "write: using painter.save_image"
                self.painter.save_image(self.path)
                if self.vrb:
                    print "write: using customkey_save"
                self.customkey_save(endkey, self.path)
        elif inp in ['s','S']:
            if self.vrb:
                print "write: using painter.save_image"
            self.painter.save_image(self.path)
            if self.vrb:
                print "write: using customkey_save"
            self.customkey_save(endkey, self.path)

    def choose_keys(self):
        '''Generater appropriate key and tests it using other classes.'''
        if self.args.customkey:
            customkey = self.customkey_load()
            if self.vrb:
                print "choose_keys: using customkey_load:", customkey
                print "choose_keys: handing custom keys over"
            return self.key.hand_over(
                customkey,
                self.painter
                )
        elif self.args.key:
            if self.vrb:
                print "choose_keys: handing preset keys over: key.preset_key"
            return self.key.hand_over(
                self.key.preset_key(self.args.key),
                self.painter
                )
        else:
            if self.vrb:
                print "choose_keys: handing False keys over: key.preset_key"
            return self.key.hand_over(
                self.key.preset_key(False),
                self.painter
                )

    def mess_over(self, txtl, key):
        '''Hands random numbers from the key.'''
        keylen = (txtl+2)/3 # 3 channels per pixel!
        if self.vrb:
            print "mess_over: computed keylen:", keylen
        endkey = r.sample(key, keylen) 
        if self.vrb:
            print "mess_over: sampled key:", endkey
        return endkey

    def customkey_load(self):
        '''Loads custom key from file. Must be stored in 1,2,3 format.'''
        if self.vrb:
            print "customkey_load: loading", self.args.customkey
        return np.loadtxt(self.args.customkey, delimiter=',')

    def customkey_save(self, customkey, path):
        '''Saves the custom key to a file in 1,2,3 format.
        Uses the same directory and filename as the image, but with .txt.
        '''
        if path.endswith('.png') or path.endswith('.PNG'):
            txtpath = path[:-4] + '.txt'
        else:
            txtpath = path + '.txt'
        if self.vrb:
            print "customkey_save: adding .txt to", txtpath
        np.savetxt(txtpath, customkey, fmt='%i', newline=',')
        if self.vrb:
            print "customkey_save: saved customkey to", txtpath

class Keymaster(object):
    '''Holds teh keys'''

    def __init__(self, vlg, pci, vrb=0):
        '''Vulgar, picture_info, verbose.'''
        self.vlg = vlg
        self.pcl = pci[0] # Picture length
        self.vrb = vrb # Verbose
        if self.vrb:
            print "Keymaster: creating instance"

    def test_txt_key(self, txtl, key, pic):
        '''Tests text and key length. Checks if it can be used for subtle or \
        vulgar encoding with given picture.
        '''
        if txtl > 3*len(key):
            raise Exception("Text is too long for this key!")
        if self.vrb:
            print "test_txt_key: testing for txt/key length: OK!"
        if self.vlg:
            pic.test_vulgar(key)
            if self.vrb:
                print "test_txt_key: testing for vulgar uses: OK!"
        else:
            pic.test_subtle(key)
            if self.vrb:
                print "test_txt_key: testing for subtle uses: OK!"

    def hand_over(self, key, pic):
        '''Hands over the keys to the higher instances.
        Finishing touches on the key.
        '''
        if self.vrb:
            print "hand_over: testing with test_txt_key"
        self.test_txt_key(0, key, pic)
        return key

    def preset_key(self, key):
        '''Chooses the appropriate key from the preset or a custom one.'''
        if type(key) == str and key.isdigit():
            if self.vrb:
                print "preset_key: checking if key is a digit: OK!"
            if self.vlg:
                if self.vrb:
                    print "preset_key: using every_vulgar with", key
                endkey = self.every_vulgar(key)
            else:
                if self.vrb:
                    print "preset_key: using every_subtle with", key
                endkey = self.every_subtle(key)
        elif key in ['x','X']:
            if self.vrb:
                print "preset_key: checking is X is chosen: OK!"
            if self.vlg:
                if self.vrb:
                    print "preset_key: using x_vulgar"
                endkey = self.x_vulgar()
            else:
                if self.vrb:
                    print "preset_key: using x_subtle"
                endkey = self.x_subtle()
        elif key == False:
            if self.vrb:
                print "preset_key: -k with no arguments: using default every"
            if self.vlg:
                if self.vrb:
                    print "preset_key: using every_vulgar(3)"
                endkey = self.every_vulgar(3)
            else:
                if self.vrb:
                    print "preset_key: using every_subtle(3)"
                endkey = self.every_subtle(3)
        else:
            raise Exception("No such key in dictionary!")
        return endkey

    def x_vulgar(self):
        '''A huge X across the picture, creating a square.'''
        endkey = []
        limit = min(self.pcl[0], self.pcl[1])
        if self.vrb:
            print "x_vulgar: setting limit to stay square:", limit
        for i in range(limit):
            endkey.append(i*self.pcl[0]+i)
            endkey.append((i+1)*self.pcl[0]-1-i)
        if self.vrb:
            print "x_vulgar: choosing unique from:", endkey
        return np.unique(endkey)

    def x_subtle(self):
        '''A subtler, more elegant X across the picture. Just kidding.'''
        endkey = []
        limit = min(self.pcl[0], self.pcl[1])
        if self.vrb:
            print "x_subtle: setting limit to stay square:", limit
        for i in range(1, limit-1, 2):
            endkey.append(i*self.pcl[0]+i)
            endkey.append((i+1)*self.pcl[0]-1-i)
        if self.vrb:
            print "x_subtle: cropping outermost rim and choosing from", endkey
        return np.unique(endkey)

    def every_vulgar(self, space):
        '''One pixel encoded in every X'''
        endkey = range(0, self.pcl[0]* self.pcl[1], int(space))
        if self.vrb:
            print "every_vulgar: generated full key:", endkey
        return endkey

    def every_subtle(self, space):
        '''One pixel in every X, in a very subtle way...'''
        xlen = self.pcl[0]
        ylen = self.pcl[1]
        picture = np.arange(xlen*ylen).reshape((ylen, xlen))[1:-1, 1:-1]
        if self.vrb:
            print "every_subtle: cropping outermost rim"
        indices = range(0, (xlen-2)*(ylen-2), int(space))
        if self.vrb:
            print "every_subtle: choosing elements of the cropped matrix", \
                  indices
        return picture.flatten()[indices]

class Painter(object):
    '''Class Painter
    Responsible for dealing with the image itself.
    '''

    def __init__(self, filename, verbose=0):
        self.img = im.open(filename)
        self.vrb = verbose
        self.size = self.img.size
        self.length = self.size[0]*self.size[1]
        if self.vrb:
            print "Painter: setting up an instance"

    def translate_matrix(self, key):
        '''Generates a matrix of x,y pixel coordinates from numeric key.'''
        matrix = []
        for i in key:
            matrix.append((int(i)%self.size[0], int(i)/self.size[0]))
        if self.vrb:
            print "translate_matrix: translated key to matrix:", matrix
        return matrix

    def test_picture(self):
        '''Tests if the picture is in appropriate format and mode.'''
        if not self.img.format in ['PNG']:
            raise Exception("Image must be a PNG!")
        elif not self.img.mode in ['RGB']:
            raise Exception("Image must be in RGB mode!")
        if self.vrb:
            print "test_picture: testing for format and mode... OK!"

    def test_picture_subtle(self):
        '''Tests if the image can be used with subtle encoding.'''
        if self.size[0] < 3 or self.size[1] < 3:
            raise Exception("Image size needs to be above 3x3 pixels!")
        if self.vrb:
            print "test_picture_subtle: testing for subtlety... OK!"

    def test_vulgar(self, key):
        '''Tests if given key can be used for vulgar encoding.'''
        if max(key) > self.length:
            raise Exception("Key beyond the image length!")
        elif len(key) > self.length:
            raise Exception("Key too long for the image!")
        if self.vrb:
            print "test_vulgar: testing for key length... OK!"            

    def test_subtle(self, key):
        '''Tests if given key and image can be used for subtle encoding.
        Consists of three parts: vulgar, rimming and vicinity tests.
        '''
        if self.vrb:
            print "test_subtle: testing for vulgarity..."
        self.test_vulgar(key)
        matrix = self.translate_matrix(key)
        if self.vrb:
            print "test_subtle: translating matrix...", matrix
        xlen, ylen = self.size[0], self.size[1]
        for i in range(len(matrix)):
            coo_x, coo_y = matrix[i]
            if coo_x in [0, xlen] or coo_y in [0, ylen]:
                raise Exception("Pixel can't be placed in the border!", \
                                (coo_x, coo_y))
            copy = np.array(matrix[:i]+matrix[i+1:])
            vicinity_x = np.array(())
            vicinity_y = np.array(())
            for j in (coo_x-1, coo_x, coo_x+1):
                vicinity_x = np.append(vicinity_x, np.where(copy[:, -1] == j))
            for j in (coo_y-1, coo_y, coo_y+1):
                vicinity_y = np.append(vicinity_y, np.where(copy[:, 0] == j))
            if bool(set(vicinity_x) & set(vicinity_y)):
                raise Exception("Pixels can't be placed less than 1 px"
                                "apart!", )
        if self.vrb:
            print "test_subtle: testing key for subtlety... OK!"

    @property
    def info(self):
        '''Public method of showing information about an image.'''
        if self.vrb:
            print "info: showing image info"
        return self.size, self.img.format, self.img.mode, \
               self.size[0]*self.size[1], \
               self.size[0]*self.size[1]-self._frame()

    def _frame(self):
        '''Displays the size of the outermost pixel frame.'''
        if self.vrb:
            print "_frame: computing outermost frame size"
        return self.size[0]*2 + self.size[1]*2 - 4

    def preview(self, matrix):
        '''Shows preview of the key in the image.'''
        for i in matrix:
            self.save_pixel(i, (255, 0, 230))
        if self.vrb:
            print "preview: modyfying file with goddamn pink pixels, PINK!"
        self.img.show()

    def postview(self):
        '''Shows image after modifications.'''
        if self.vrb:
            print "postview: just showing the image"
        self.img.show()

    def read_vulgar(self, matrix):
        '''Reads the pixels by key'''
        pixels = []
        for i in matrix:
            pixels.append(self.img.getpixel(i))
        if self.vrb:
            print "read_vulgar: reading pixels one-by-one:", pixels
        return pixels

    def read_subtle(self, matrix):
        '''Reads the pixels and their vicinity by key.'''   
        pixels = np.empty((len(matrix), 2, 3))
        for i in range(len(matrix)):
            coo_x = matrix[i][0]
            coo_y = matrix[i][1]
            vinc_idx = (
                (coo_x-1, coo_y-1), (coo_x-1, coo_y), (coo_x-1, coo_y+1),
                 (coo_x, coo_y-1),                     (coo_x, coo_y+1),
                (coo_x+1, coo_y-1), (coo_x+1, coo_y), (coo_x+1, coo_x+1)
                )
            vincinity = []
            for j in vinc_idx:
                vincinity.append(self.img.getpixel(tuple(j)))
                # There is virtually NO POINT in returning the whole list,
                # when we're interested only in the middle point and the
                # mean of the others, is it?
            channels = np.empty(3)
            for k in range(3):
                channels[k] = np.mean(vincinity[k])
            pixels[i, 0] = np.array(channels)
            pixels[i, 1] = np.array(self.img.getpixel((coo_x, coo_y)))
        if self.vrb:
            print "read_subtle: reading pixels one-by-one"
            print "[[[meanCH1,meanCH2,meanCH3],[xyCH1,xyCH2,xyCH3]]..."
        return pixels

    def save_pixel(self, place, color):
        '''Saves one pixel of a given color at the given location.'''
        channels = (
            int(color[0]),int(color[1]),int(color[2]))
        if self.vrb:
            print "save_pixel: changing one pixel {!s} at {!s}:".format(\
                channels, place)
        self.img.putpixel(place, channels)

    def save_image(self, location):
        '''Saves the modified file at the given location.'''
        if self.vrb:
            print "save_image: saving the location"
        self.img.save(location)


class Coder(object):
    '''Encodes and decodes text into pixels.
    Key is a simple list of pixel indices.
    '''

    def __init__(self, vrb=0):
        self.vrb = vrb
        self.rawtext = []
        self.rawpix = []
        if self.vrb:
            print "Coder: setting up instance"

class VulgarCoder(Coder):
    '''Encodes and decodes using vulgar methods.'''

    def encode(self, text, painting, matrix):
        '''Encodes text into pixels using vulgar methods.'''
        self.rawtext = list(text)
        if self.vrb:
            print "vulgar.encode: encoding:", self.rawtext
        channels = []
        for i in self.rawtext:
            # Adding 63 to average the vulgarity
            channels.append(ord(i)+63)
        if self.vrb:
            print "vulgar.encode: encoding every letter into a channel"
        remainder = 3 - (len(channels) % 3)
        if remainder != 0:
            channels += [63]*remainder
            if self.vrb:
                print "vulgar.encode: generating additional empty channels", \
                    remainder
        for i in range(0, len(channels), 3):
            single_px = []
            for j in range(3):
                single_px.append(channels[i+j])
            self.rawpix.append(single_px)
            place = matrix[i/3]
            painting.save_pixel(place, single_px)
        if self.vrb:
            print "vulgar.encode: pixels encoded"

    def decode(self, painting, matrix):
        '''Decodes pixels to text using vulgar methods.'''
        pixels = painting.read_vulgar(matrix)
        if self.vrb:
            print "vulgar.decode: computed matrix:", pixels
        for i in pixels:
            for j in i:
                self.rawpix.append(j)
        if self.vrb:
            print "vulgar.decode: flattened matrix"
        for i in self.rawpix:
            print i
            # Substracting 63 to average the vulgarity
            self.rawtext.append(chr(i-63))
        if self.vrb:
            print "vulgar.decode: decoding matrix", str(self.rawtext)
        return ''.join(self.rawtext)

class SubtleCoder(Coder):
    '''Encodes and decodes using subtle methods.'''

    def encode(self, text, painting, matrix):
        '''Encodes text into pixels using subtle methods.'''
        self.rawtext = list(text)
        if self.vrb:
            print "subtle.encode: encoding text:", self.rawtext
        channels = []
        for i in self.rawtext:
            channels.append(128-ord(i))
        if self.vrb:
            print "subtle.encode: encoding every letter into a channel", \
                channels
        remainder = 3 - (len(channels) % 3)
        if remainder != 0:
            channels += [0]*remainder
            if self.vrb:
                print "subtle.encode: generating additional empty channels", \
                    remainder
        neighbourhoods = painting.read_subtle(matrix)
        if self.vrb:
            print "subtle.encode: acquiring neighbourhoods"
        for i in range(0, len(channels), 3):
            single_px = []
            for j in range(3):
                vicinity = neighbourhoods[i/3][0][j]
                if vicinity <= 127:
                    single_px.append(vicinity+channels[i+j])
                else:
                    single_px.append(vicinity-channels[i+j])
            self.rawpix.append(single_px)
            place = matrix[i/3]
            painting.save_pixel(place, single_px)
        if self.vrb:
            print "subtle.encode: pixels encoded"

    def decode(self, painting, matrix):
        '''Decodes pixels to text using subtle methods.'''
        neighbourhoods = painting.read_subtle(matrix)[:, 0]
        if self.vrb:
            print "subtle.decode: acquire neighbourhoods"
        self.rawpix = painting.read_subtle(matrix)[:, 1]
        if self.vrb:
            print "subtle.decode: acquire list of pixels"
        for i in range(len(self.rawpix)):
            for j in range(3):
                vicinity = neighbourhoods[i, j]
                if vicinity <= 127:
                    channel = chr(int(128-(self.rawpix[i, j]-vicinity)))
                else:
                    channel = chr(int(128-(vicinity-self.rawpix[i, j])))
                self.rawtext.append(channel)
        if self.vrb:
            print "subtle.decode: pixels encoded:", str(self.rawtext)
        return ''.join(self.rawtext)

if __name__ == '__main__':
    Overlord()
