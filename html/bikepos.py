from flask import Flask, request, send_from_directory
from flask import jsonify
from flask_cors import CORS, cross_origin
import model
from pony.orm import db_session, Database
import time

app = Flask(__name__, static_url_path='')

CORS(app)


model.db.bind('sqlite', 'bikes.sqlite', create_db=False)
model.db.generate_mapping(create_tables=False)



@app.route('/static/bike_pos')
def bike_pos():
    with db_session:    
        b = model.Bike[1]
    
    return jsonify(bike_pos={'latitude': "%.20s" % b.lat,
                             'longitude': "%.20s" % b.lon},
                   message='success',
                   timestamp=str(time.time()).split('.')[0])



@app.route('/static/<path:path>')
def send(path):
    return send_from_directory('static', path)
