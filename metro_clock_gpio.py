#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import os
import time
import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM)

STBY = 27 #Standby
PWM = 22 #Speed control 
IN1 = 23 #Direction
IN2 = 24 #Direction

GPIO.setup(IN1, GPIO.OUT)
GPIO.setup(IN2, GPIO.OUT)
GPIO.setup(PWM, GPIO.OUT)
GPIO.setup(STBY, GPIO.OUT)
pwm_instance = GPIO.PWM(PWM, 1000)
# direction_file = "/home/metronaytto/projects/metro_display/direction.txt"

def move(direction):
    GPIO.output(STBY, GPIO.HIGH) #disable standby
    inPin1 = GPIO.LOW
    inPin2 = GPIO.HIGH

    if direction == 1:
        inPin1 = GPIO.HIGH
        inPin2 = GPIO.LOW

    GPIO.output(IN1, inPin1)
    GPIO.output(IN2, inPin2)
    pwm_instance.start(100)
    time.sleep(0.5)
    pwm_instance.stop()
    GPIO.output(STBY, GPIO.LOW) #enable standby
    print("moved to direction: ", direction)

try:
    # file = open(direction_file, "r")
    # direction = file.read()
    # file.close()
    direction = os.getenv('CLOCK_DIRECTION')
    if direction == "1":
        move(1)
        # file = open(direction_file, "w")
        # file.write("0")
        # file.close()
        os.environ['CLOCK_DIRECTION'] = '0'
    else:
        move(0)
        # file = open(direction_file, "w")
        # file.write("1")
        # file.close()
        os.environ['CLOCK_DIRECTION'] = '1'

except Exception as e:
    print(e)

finally:
    GPIO.cleanup()
    
