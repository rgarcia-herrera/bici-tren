from jinja2 import Environment, FileSystemLoader
from flask import Flask, send_from_directory
from flask import jsonify, Response, request
from flask_cors import CORS
import svgwrite

import bike_agent as model

from pprint import pprint

app = Flask(__name__, static_url_path='')

app.secret_key = 'F12Zr47j\3yX R~X@H!jmM]Lwf/,?KT'
CORS(app)

model.connect('mydb')

env = Environment(loader=FileSystemLoader('templates'))


@app.route('/map')
def map():
    template = env.get_template('map.html')
    return Response(template.render())


@app.route('/bike/<bike_id>/<destination_heading>_marker.svg')
def bike_marker(bike_id, destination_heading):
    b = model.Bike.objects.with_id(bike_id)
    return Response(b.marker(),
                    mimetype="image/svg+xml")


@app.route('/bike/<bike_id>/map')
def get_map(bike_id):
    template = env.get_template('map.html')
    return Response(template.render(bike_id=bike_id))


@app.route('/bike/<bike_id>')
def get_bike(bike_id):
    b = model.Bike.objects.with_id(bike_id)
    return jsonify(b.to_dict())


@app.route('/bikes_in/')
def bikes_in():
    return jsonify([b.to_dict() for b in model.Bike.objects(
        point__geo_within_box=[(float(request.args.get('sw_lng')),
                                float(request.args.get('sw_lat'))),
                               (float(request.args.get('ne_lng')),
                                float(request.args.get('ne_lat')))])])


@app.route('/static/<path:path>')
def send(path):
    return send_from_directory('static', path)


def marker(headings):
    """
    returns svg with nice arrows
    TODO: not implemented
    """
    dwg = svgwrite.Drawing()
    dwg.viewbox(width=100, height=100)
    dh = svgwrite.shapes.Polygon(points=[[50, 20],
                                         [30, 80],
                                         [70, 80]],
                                 fill='blue', opacity=0.6)
    dh.rotate(self.destination_heading,
    center=(50, 50))

    h = svgwrite.shapes.Polygon(points=[[50, 30],
                                        [35, 75],
                                        [65, 75]],
                                fill='yellow',
                                opacity=0.44,
                                stroke="green",
                                stroke_width=1,
                                stroke_opacity=1)
    h.rotate(self.heading,
             center=(50, 50))
    dwg.add(dh)
    dwg.add(h)

    return dwg.tostring()
