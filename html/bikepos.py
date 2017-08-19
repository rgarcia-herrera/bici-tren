from flask import Flask, request, send_from_directory
from flask import jsonify
from flask_cors import CORS, cross_origin

app = Flask(__name__, static_url_path='')

CORS(app)

@app.route('/static/bike_pos')
def bike_pos():
    return jsonify(bike_pos={'latitude': 51.30821712059571,
                             'longitude': -137.97789451785653},
                   message='success',
                   timestamp=1503184437)



@app.route('/static/<path:path>')
def send(path):
    return send_from_directory('static', path)
