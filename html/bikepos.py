from jinja2 import Environment, FileSystemLoader
from flask import Flask, send_from_directory
from flask import jsonify, Response
from flask_cors import CORS

import model

from pprint import pprint

app = Flask(__name__, static_url_path='')

app.secret_key = 'F12Zr47j\3yX R~X@H!jmM]Lwf/,?KT'
CORS(app)

model.connect('mydb')

env = Environment(loader=FileSystemLoader('templates'))


@app.route('/bike/<bike_id>/marker')
def bike_marker(bike_id):
    b = model.Bike.objects.with_id(bike_id)
    return Response(b.marker(), mimetype="text/xml")


@app.route('/bike/<bike_id>/map')
def get_map(bike_id):
    template = env.get_template('map.html')
    return template.render(bike_id=bike_id)


@app.route('/bike/<bike_id>')
def get_bike(bike_id):
    b = model.Bike.objects.with_id(bike_id)
    return jsonify(b.to_dict())


@app.route('/static/<path:path>')
def send(path):
    return send_from_directory('static', path)
