#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from serial import Serial
from time import sleep
import urllib
import string
from bs4 import BeautifulSoup
import time

ser = Serial("/dev/ttyUSB0", 600, 7, 'E', 1)
STX = chr(2)
ETX = chr(3)
EOT = chr(4)
ENQ = chr(5)
NL = chr(13)
PAD = chr(127)

addr = "01" # low bit says write

def wr(x):
	#ser.write(x) # pad bytes seem necessary
	ser.write(PAD + PAD + x + PAD + PAD) # nl is not needed
	#ser.write(PAD + PAD + x + PAD + PAD + NL) # though works with it too

slp = 1 # sometimes even smaller works, sometimes need to retry with this

while 1:            
	f = urllib.urlopen("http://sakari.nerdclub.fi/dist/php/message.html")
	soup = BeautifulSoup(f)
	print soup
	print "\n" 
	message = repr(soup.body)
	print message
	print "\n"
	message = message.replace("ä", chr(123))
	message = message.replace("ö", chr(124))
	message = message.replace("å", chr(125))
	message = message.replace("Ä", chr(91))
	message = message.replace("Ö", chr(92))
	message = message.replace("Å", chr(93))
	message = message.replace("&lt;", "<")
	message = message.replace("&gt;", ">")
	message = message.replace("&amp;", "&")
	message = message.replace("ü", chr(126))
	message = message.replace("Ü", chr(94))

	
	print message
	message = message.strip('<body>')
	message = message.strip('</body>')
	print message
	rows = message.split('<br/>')

	if len(rows) == 2:
		print rows[0]
		# display text immediately 1st row
		# version?
		# sbn: text type
		# lrmz: left right middle something
		wr(EOT)
		sleep(slp)
		wr(addr + ENQ)
		sleep(slp)
		row = "1" # 1=top, 2=bottom, 3=clock
		side = "2" # wtf?
		# b=caps, s=big spaces, n=big text
		wr(STX + row + side + "000nlT" + rows[0] + ETX + "p")
		sleep(slp)
		wr(EOT)
		
		print rows[1]
		# display text immediately 2nd row
		wr(EOT)
		sleep(slp)
		wr(addr + ENQ)
		sleep(slp)
		row = "2" # 1=top, 2=bottom, 3=clock
		# b=caps, s=big spaces, n=big text
		wr(STX + row + side + "000nlT" + rows[1] + ETX + "p")
		sleep(slp)
		wr(EOT)
		print "ok"
	
	elif len(rows) == 1:
		rows[0] = rows[0].strip('<br')
		# display text immediately 1st row
		# version?
		# sbn: text type
		# lrmz: left right middle something
		wr(EOT)
		sleep(slp)
		wr(addr + ENQ)
		sleep(slp)
		row = "1" # 1=top, 2=bottom, 3=clock
		side = "2" # wtf?
		# b=caps, s=big spaces, n=big text
		wr(STX + row + side + "000nlT" + rows[0] + ETX + "p")
		sleep(slp)
		wr(EOT)

		# display text immediately 2nd row
		wr(EOT)
		sleep(slp)
		wr(addr + ENQ)
		sleep(slp)
		row = "2" # 1=top, 2=bottom, 3=clock
		# b=caps, s=big spaces, n=big text
		wr(STX + row + side + "000nlT" + "  " + ETX + "p")
		sleep(slp)
		wr(EOT)
		print "ok"

	else:
		sleep(slp)

	
	sleep(5)

