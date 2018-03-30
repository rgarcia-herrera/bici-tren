import agent as model
import argparse
import json
from LatLon import LatLon, Latitude, Longitude

parser = argparse.ArgumentParser(
    description='ride bike at speed thru route')

parser.add_argument('--route', type=argparse.FileType('r'), required=True,
                    help='A BRouter route in geojson format.')
parser.add_argument('--speed', default=3.0, type=float,
                    help='speed in meters per second, default=3.0')

args = parser.parse_args()


model.db.bind(provider='sqlite', filename=':memory:', create_db=True)
model.db.generate_mapping(create_tables=True)

route = json.loads(args.route.read())
coords = [[c[0], c[1]]
          for c in route['features'][0]['geometry']['coordinates']]

start = LatLon(Latitude(coords[0][0]),
               Longitude(coords[0][1]))

end = LatLon(Latitude(coords[-1][0]),
             Longitude(coords[-1][1]))


with model.orm.db_session:
    b = model.Agent()
    b.set_point(start)
    b.set_destination(end)
    b.speed = args.speed
