# -*- coding: UTF-8 -*-

from serial import Serial
from serial import serialutil
from time import sleep
import urllib.request
from bs4 import BeautifulSoup

try:
    ser = Serial("/dev/ttyUSB0", 600, 7, 'E', 1)
except serialutil.SerialException:
    try:
        ser = Serial("/dev/ttyUSB1", 600, 7, 'E', 1)
    except serialutil.SerialException:
        print("No serial device found")

STX = chr(2)
ETX = chr(3)
EOT = chr(4)
ENQ = chr(5)
NL = chr(13)
PAD = chr(127)
addr = "01"  # low bit says write
slp = 1  # sometimes even smaller works, sometimes need to retry with this
side = "2"  # wtf?


def replace_scand_chars(message):
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
    message = message.replace("É", chr(64))
    message = message.replace("é", chr(96))
    return message


def wr(x):
    ser.write(bytes(PAD + PAD + x + PAD + PAD, "UTF-8"))  # nl is not needed
    # ser.write(PAD + PAD + x + PAD + PAD + NL) # though works with it too


def write_row(message, row):
    wr(EOT)
    sleep(slp)
    wr(addr + ENQ)
    sleep(slp)
    # b=caps, s=big spaces, n=big text
    wr(STX + row + side + "000nlT" + message + ETX + "p")
    sleep(slp)
    wr(EOT)


while 1:
    f = urllib.request.urlopen("http://localhost/dist/php/message.html")
    soup = BeautifulSoup(f)
    message = repr(soup.body)
    message = replace_scand_chars(message)
    message = message.strip('<body>')
    message = message.strip('</body>')
    rows = message.split('<br/>')

    if len(rows) == 2:
        print(rows[0])
        # display text immediately 1st row
        write_row(rows[0], "1")
        print(rows[1])
        # display text immediately 2nd row
        write_row(rows[1], "2")
        print("ok")

    elif len(rows) == 1:
        rows[0] = rows[0].strip('<br')
        # display text immediately 1st row
        write_row(rows[0], "1")

        # display text immediately 2nd row
        write_row(" ", "2")
        print("ok")

    sleep(5)
