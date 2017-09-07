from flask import Flask
from flask_mongoengine import MongoEngine

from flask import Flask, request, send_from_directory, session
from flask import jsonify

from flask_cors import CORS, cross_origin
import model

import time
import json
import urllib2


from pprint import pprint

app = Flask(__name__, static_url_path='')

app.secret_key = 'F12Zr47j\3yX R~X@H!jmM]Lwf/,?KT'
CORS(app)

db = MongoEngine(app)


route_url = "http://h2096617.stratoserver.net:443/brouter?lonlats=%s,%s|%s,%s&profile=trekking&alternativeidx=0&format=geojson"
# some random start and end points
route = json.loads(urllib2.urlopen(route_url % (-99.120,
                                                    19.410,
                                                    -99.137,
                                                    19.435)).read())
coords = route['features'][0]['geometry']['coordinates']


@app.route('/static/bike_pos')
def bike_pos():

    with db_session:
        b = model.Bike[1]

    return jsonify(bike_pos={'latitude': b.lat,
                             'longitude': b.lon},
                   message='success',
                   timestamp=str(time.time()).split('.')[0])



@app.route('/static/<path:path>')
def send(path):
    return send_from_directory('static', path)
