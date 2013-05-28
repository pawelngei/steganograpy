#!/usr/bin/env python2.7
# Copyleft by Pawel Chojnacki

__author__ = 'Pawel "duskglow" Chojnacki'
__copyright__ ='Copyleft 2013 Pawel Chojnacki'
__version__ = '0.0.1'
__date__ = '14.05.2013'
__license__ = 'GPLv3'

import Image as im # Image manipulation
import argparse as ap
#~ import sys # Is it really needed?
import numpy as np
# biblioteka od szyfrowania

class Overlord(object):
	
	def __init__(self):
		# Responsible for interacting with the user and creating new classes
		options = ap.ArgumentParser(
									prog="stegnograPy",
									description="A simple python program to hide text inside pictures. Supported formats are")
		#~ Subparsers? Is it a good way?
		#~ mode = options.add_subparsers()
		#~ infoarg = mode.add_parser('info',help="show information about image") # TO IMPROVE, clearly stated
		#~ readarg = mode.add_parser('read',help="decode text from image")
		#~ writearg = mode.add_parser('write',help="encode text into image")
		options.add_argument("image",help="path to image")
		mode = options.add_mutually_exclusive_group(required=True)
		mode.add_argument("-I","--info",action="store_true",help="show information about image")
		mode.add_argument("-R","--read",action="store_true",help="decode text from image")
		mode.add_argument("-W","--write",type=str,help="encode text into image")
		encoding = options.add_mutually_exclusive_group()
		encoding.add_argument("-u","--vulgar",action="store_true",help="vulgar encoding alghoritm")
		encoding.add_argument("-s","--subtle",action="store_true",help="subtle encoding alghoritm")
		options.add_argument("-k","--key",help="key used to choose encoded pixels")
		options.add_argument("-c","--encryption",help="encryption password")
		volume = options.add_mutually_exclusive_group()
		volume.add_argument("-v", "--verbose", action="store_true", default=0, help="verbose mode: print it all!")
		volume.add_argument("-q", "--quiet", action="store_true", default=0, help="quiet mode: shhhh!")
		args = options.parse_args()
		
		print args
		
		if args.info:
			pass
			km = Keymaster('info')
		elif args.read:
			pass
			km = Keyaster('read',key=args.key)
		elif args.write:
			pass
			#~ km = Keymaster('write',key=args.key)
			#~ km.write(text)
		
		# Sprawdzic, czy args.image jest obrazkiem
		#~ img = Image(args.image)
		
		
		
	
	
	
	
	# CASE SENSITIVE FILENAMES
	pass
	
class Keymaster(object):
	
	def __init___(self,mode,text=0,key=0):
		pass
		
	def __new__(self,mode,text=0,key=0):
		pass
	# Manager and keymaster
	
	pass
	
class Image(object):
	# Responsible for manipulating the image itself
	
	def __init__(self,fname,**args):
		# sprawdzenie, czy obrazek istnieje -> do kontrolera
		# sprawdzenie, czy jest obrazem
		self.i = im.show(fname)
		self.f = self.i.format()
		self.s = self.i.size()
		self.m = self.i.mode()
		
	@property
	def info(self):
		'''Wystwietla informacje o obrazku'''
		return self.f, self.s, self.m
	
	def podglad(self,key):
		# key to lista pikseli obliczona w keymasterze
		pass
	
	def odczytaj(self,key):
		# self.i.getpixel(x,y)
		pass
	
	def zapisz(self,key,text):
		# text in the form of a tuple
		# self.i.putpixel(x,y,color)
		pass
	
class Encode(object):
	pass
	
class Vulgar(Encode):
	pass
	
class Subtle(Encode):
	pass

class Encrypt(object):
	pass

if __name__ == '__main__':
	Overlord()
