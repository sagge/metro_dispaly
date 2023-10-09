#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import schedule
import time
from threading import Event
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

exit = Event()

direction = 0

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

def move_and_update_direction():
    global direction
    if direction == 1:
        move(1)
        direction = 0
    else:
        move(0)
        direction = 1

def main():
    schedule.every().minute.at(':00').do(move_and_update_direction)
    while not exit.is_set():
        schedule.run_pending()
        time.sleep(.1)

    print("All done!")
    GPIO.cleanup()

def quit(signo, _frame):
    print("Interrupted by %d, shutting down" % signo)
    exit.set()

if __name__ == '__main__':

    import signal
    for sig in ('TERM', 'HUP', 'INT'):
        signal.signal(getattr(signal, 'SIG'+sig), quit);

    main()