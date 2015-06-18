
import time
import sys
from datetime import datetime

from flask import Flask
from flask import jsonify

from MiLight import *


app = Flask(__name__)

ml = Milight()

@app.route("/all/on")
def all_on():
    ml.on()
    return jsonify({
        'response' : 'ok'
    })

@app.route("/all/off")
def all_off():
    ml.off()
    return jsonify({'response' : 'ok'})

@app.route("/all/white")
def all_white():
    ml.setwhite()
    return jsonify({'response' : 'ok'})


@app.route("/all/brightness/<int:val>")
def all_brightness(val):
    ml.setbrightness(val)
    return jsonify({'response' : 'ok'})

@app.route("/all/color/<int:val>")
def all_color(val):
    ml.setcolor(val)
    return jsonify({'response' : 'ok'})


if __name__ == "__main__":
    app.run(debug=True)