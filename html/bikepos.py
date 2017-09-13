from flask import Flask, send_from_directory
from flask import jsonify
from flask_cors import CORS, cross_origin

import model
import time

from pprint import pprint

app = Flask(__name__, static_url_path='')

app.secret_key = 'F12Zr47j\3yX R~X@H!jmM]Lwf/,?KT'
CORS(app)

model.connect('mydb')


@app.route('/static/bike_pos/<bike_id>')
def bike_pos(bike_id):

    b = model.Bike.objects.with_id(bike_id)
    return jsonify(bike_pos={'latitude': b.point[0],
                             'longitude': b.point[1]},
                   message='success',
                   timestamp=str(time.time()).split('.')[0])


@app.route('/static/<path:path>')
def send(path):
    return send_from_directory('static', path)
