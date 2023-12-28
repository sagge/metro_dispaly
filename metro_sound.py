#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from serial import Serial
from time import sleep
import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM)

RELAY = 2
GPIO.setup(RELAY, GPIO.OUT)

# Connect speaker relay
GPIO.output(RELAY, GPIO.LOW)

ser = Serial("/dev/ttyUSB_SOUND", 9600, 8, 'N', 1)

sleep(0.1)
ser.write(b"@I.@E-.")
sleep(0.1)
ser.write(b"@E+.")
sleep(0.1)
ser.write(b"@E+.")
sleep(0.1)
ser.write(b"@E+.")
sleep(0.1)
ser.write(b"RL.")
sleep(8)

# Disconnect speaker relay
GPIO.output(RELAY, GPIO.HIGH)
sleep(0.5)