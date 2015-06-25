
import time
import sys
from datetime import datetime, timedelta

from flask import Flask, send_from_directory, jsonify, Response
from flask.ext.cors import CORS
from flask.ext.aiohttp import AioHTTP
from apscheduler.schedulers.background import BackgroundScheduler
import requests

from MiLight import *

app = Flask(__name__)
#CORS(aio, resources=r'/api/*', allow_headers='Content-Type')
aio = AioHTTP(app)

ml = Milight()

DEBUG_WEB = False
WEB_SERVER = 'http://localhost:3000/'



def serve_web(url):
    if url == "":
        url = "index.html"

    if DEBUG_WEB:
        url = WEB_SERVER + url
        res = requests.get(url)
        return Response(res.content, res.headers['Content-Type'])
    else:
        return send_from_directory('web/dist', url)

def do_alarm():
    with app.app_context():
        print("Alarm at %s" % datetime.now())
        ml.whitetransition(25, 60)
        
        # Do whatever you were doing to check the second API

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
                ml.set_white()

            elif elem2 == 'nightmode':
                ml.nightmode()

            elif elem2 == 'discomode':
                ml.discomode()

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
        elif elems1 == 'alarm':
            time           = elems[2]
            dtalarm        = datetime.now()
            dtalarm = dtalarm.replace(hour = int(time[0:2]), minute = int(time[2:4]), second=0)

            if dtalarm < datetime.now():
                dtalarm += timedelta(days=1)

            timediff = dtalarm - datetime.now()

            apsched = BackgroundScheduler()
            apsched.start()

            print("Scheduling alarm for %s (%ss from now)" % (dtalarm, timediff.seconds))
            apsched.add_job(do_alarm, 'date', run_date=dtalarm, id='wakeup')
            apsched.print_jobs()
            ml.whitetransition(2, 5)
            ml.off()
            return "Scheduled for %s" % time


        elif elems1 == 'ip':
            ml.set_ip(elems[2])
            return "ok"
        else:
            return "not found", 404

    else:
        return serve_web(url)


if __name__ == "__main__":
    aio.run(app, debug=True, host="0.0.0.0")