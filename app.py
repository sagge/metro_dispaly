# -*- coding: UTF-8 -*-

from serial import Serial
from serial import serialutil
import argparse
import gunicorn.app.base
import os
import threading
from time import sleep
import RPi.GPIO as GPIO

from flask import Flask, request
from flask_expects_json import expects_json
from flask_cors import CORS
from multiprocessing import Manager


app = Flask(__name__)
CORS(app)

schema = {
    'type': 'object',
    'properties': {
        '1': {'type': 'string', 'maxLength': 48},
        '2': {'type': 'string', 'maxLength': 48},
    },
    'required': ['1', '2']
}

schema2 = {
    'type': 'object',
    'properties': {
        'buttonValue': {'type': 'string', 'maxLength': 48},
    },
    'required': ['buttonValue']
}


@app.route('/', methods=['GET'])
def get_data():
    global data
    return_value = {1: data['rows']
                    [1], 2: data['rows'][2]}
    return return_value, 200


@app.route('/', methods=['PUT'])
@expects_json(schema)
def update_data():
    global data
    json_data = request.json
    data['rows'][1] = json_data["1"]
    data['rows'][2] = json_data["2"]
    return_value = {1: data['rows']
                    [1], 2: data['rows'][2]}
    return return_value, 200

@app.route('/sound', methods=['PUT'])
@expects_json(schema2)
def play_sound():
    json_data = request.json
    value = json_data["buttonValue"]
    allowed_values = set(["IK", "KP", "MM", "RL", "S1", "VS"])

    if not value in allowed_values:
        return "Invalid value", 400

    RELAY = 2
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(RELAY, GPIO.OUT)
    # Connect speaker relay
    GPIO.output(RELAY, GPIO.LOW)

    command = value + "."

    try:
        ser = Serial("/dev/ttyUSB_SOUND", 9600, 8, 'N', 1)
    except serialutil.SerialException:
        return "Serial device disconnected", 500

    sleep(0.1)
    ser.write(b"@I.@E-.")
    sleep(0.1)
    ser.write(b"@E+.")
    sleep(0.1)
    ser.write(b"@E+.")
    sleep(0.1)
    ser.write(b"@E+.")
    sleep(0.1)
    ser.write(command)
    return "ok", 200

def __worker_thread():
    global data
    current_row1 = data['rows'][1]
    current_row2 = data['rows'][2]
    try:
        ser = Serial("/dev/ttyUSB_TEXT", 600, 7, 'E', 1)
    except serialutil.SerialException:
        try:
            ser = Serial("/dev/ttyUSB0", 600, 7, 'E', 1)
        except serialutil.SerialException:
            print("No serial device found")

    STX = chr(2)
    ETX = chr(3)
    EOT = chr(4)
    ENQ = chr(5)
    NL = chr(13)
    PAD = chr(127)
    addr = "01"
    slp = 1  # sometimes even smaller works, sometimes need to retry with this
    side = "2"

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
        # nl is not needed
        ser.write(bytes(PAD + PAD + x + PAD + PAD, "UTF-8"))
        # ser.write(PAD + PAD + x + PAD + PAD + NL) # though works with it too

    def write_row(message, row):
        wr(EOT)
        sleep(slp)
        wr(addr + ENQ)
        sleep(slp)
        wr(STX + row + side + "000nlT" + message + ETX + "p")
        sleep(slp)
        wr(EOT)

    while True:
        # Stupid hack to poll for changes...
        for i in range(100):
            if current_row1 == data['rows'][1] and current_row2 == data['rows'][2]:
                sleep(0.1)
            else:
                break

        row_to_be_set1 = data['rows'][1]
        row_to_be_set2 = data['rows'][2]
        print(row_to_be_set1)
        print(row_to_be_set2)

        if row_to_be_set1:
            write_row(replace_scand_chars(row_to_be_set1), "1")

        if row_to_be_set2:
            write_row(replace_scand_chars(row_to_be_set2), "2")

        current_row1 = row_to_be_set1
        current_row2 = row_to_be_set2


# App Initialization
def initialize():
    global data
    data = {}
    data['master_pid'] = os.getpid()
    manager_dict = Manager().dict()
    manager_dict[1] = 'row1'
    manager_dict[2] = 'row2'
    data['rows'] = manager_dict

    # For the background thread
    t = threading.Thread(target=__worker_thread)
    t.daemon = True
    t.start()
    data['background_thread'] = t


# Custom Gunicorn application: https://docs.gunicorn.org/en/stable/custom.html
class HttpServer(gunicorn.app.base.BaseApplication):
    def __init__(self, app, options=None):
        self.options = options or {}
        self.application = app
        super().__init__()

    def load_config(self):
        config = {key: value for key, value in self.options.items()
                  if key in self.cfg.settings and value is not None}
        for key, value in config.items():
            self.cfg.set(key.lower(), value)

    def load(self):
        return self.application


if __name__ == '__main__':
    global data
    parser = argparse.ArgumentParser()
    parser.add_argument('--num-workers', type=int, default=2)
    parser.add_argument('--port', type=str, default='8080')
    args = parser.parse_args()
    options = {
        'bind': '%s:%s' % ('0.0.0.0', args.port),
        'workers': args.num_workers,
    }
    initialize()
    HttpServer(app, options).run()
