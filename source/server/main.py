import time
from subprocess import call
from flask import Flask, jsonify, request
import json
from flask_cors import CORS
from gevent import pywsgi
import sys

app = Flask(__name__)
CORS(app)


class Room:
    name: str
    password: str
    lastUpdateClientTime: float
    lastUpdateServerTime: float
    playbackRate: float
    currentTime: float
    paused: bool
    url: str
    duration: float

    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)


database = dict()


def generateErrorResponse(errorMessage):
    return jsonify({"errorMessage": errorMessage})


@app.route('/room/get', methods=["get"])
def getRoom():
    name = request.args["name"]
    if(name not in database):
        return generateErrorResponse("房间不存在")
    return jsonify(database[name].__dict__)


@app.route('/timestamp', methods=["get"])
def getTimestamp():
    return jsonify({"timestamp": time.time()})


@app.route('/room/update', methods=["get"])
def updateRoom():
    room = Room()
    room.name = request.args["name"]
    room.password = request.args["password"]

    if room.name in database:
        print(database[room.name].__dict__)
        if database[room.name].password != room.password:
            return generateErrorResponse("密码错误")

    room.playbackRate = request.args["playbackRate"]
    room.currentTime = float(request.args["currentTime"])
    room.paused = request.args["paused"] != "false"
    room.url = request.args["url"]
    room.lastUpdateClientTime = request.args["lastUpdateClientTime"]
    if "duration" not in request.args:
        room.duration = 1e9
        # return generateErrorResponse("需要升级，点击帮助按钮获取更新")
    else:
        room.duration = float(request.args["duration"])
    room.lastUpdateServerTime = time.time()

    database[room.name] = room
    sys.stdout.flush()
    sys.stderr.flush()
    return jsonify(room.__dict__)


if __name__ == '__main__':
    if(sys.argv[1] == "debug"):
        app.debug = False
        app.run(host='0.0.0.0')

    if(sys.argv[1] == "prod"):
        server = pywsgi.WSGIServer(
            ('0.0.0.0', 5000), app,  keyfile='private.key', certfile='certificate.crt')
        server.serve_forever()
