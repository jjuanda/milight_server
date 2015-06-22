
import time
import sys
from datetime import datetime

from flask import Flask, send_from_directory, jsonify, Response
from flask.ext.cors import CORS

import requests

from MiLight import *

app = Flask(__name__)
CORS(app, resources=r'/api/*', allow_headers='Content-Type')


ml = Milight()

DEBUG_WEB = True
WEB_SERVER = 'http://localhost:3000/'

def serve_web(url):
    if url == "":
        url = "index.html"

    if DEBUG_WEB:
        url = WEB_SERVER + url
        print(url)
        res = requests.get(url)
        return Response(res.content, res.headers['Content-Type'])
    else:
        print("web/dist%s" % url)
        return send_from_directory('web/dist', url)

@app.route("/")
def index():
    return serve_web('')


@app.route("/<path:url>", methods=['GET', 'POST'])
def proxy(url):
    elems = url.split('/')
    lelems = len(elems)

    if lelems > 0 and elems[0] == 'api':
        elems1 = elems[1]
        if elems1 == 'all':
            elem2 = elems[2]
            if elem2 == 'on':
                ml.on()

            elif elem2 == 'off':
                ml.off()

            elif elem2 == 'white':
                ml.setwhite()

            elif elem2 == 'brightness':
                print(elems)
                ml.set_brightness(int(elems[3]))

            elif elem2 == 'color':
                ml.set_hex_color(elems[3])

            elif elem2 == 'hue':
                ml.set_color(elems[3])

            elif elem2 == 'transition':
                if elem[3] == 'white':
                    time = elems[4]
                    brightness = elems[5]
                    ml.whitetransition(brightness, time)
            return "ok"
        elif elems1 == 'ip':
            ml.set_ip(elems[2])
            return "ok"
        else:
            return "not found", 404

    else:
        return serve_web(url)


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")