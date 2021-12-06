#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from serial import Serial
import time

ser = Serial('/dev/ttyUSB1', 9600)
time.sleep(2)
file = open("/home/pi/projects/metro_display/direction.txt", "r")
direction = file.read()
file.close()
print(direction)
if direction == "0":
    ser.write(bytes('e', "UTF-8"))
    print("wrote")
    msg = ser.readline()
    print(msg)
    file = open("/home/pi/projects/metro_display/direction.txt", "w")
    file.write("1")
    file.close()
elif direction == "1":
    ser.write(bytes('t', "UTF-8"))
    print("wrote")
    msg = ser.readline()
    print(msg)
    file = open("/home/pi/projects/metro_display/direction.txt", "w")
    file.write("0")
    file.close()
else:
    file = open("/home/pi/projects/metro_display/direction.txt", "w")
    file.write("0")
    file.close()
