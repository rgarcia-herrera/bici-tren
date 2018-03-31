import bike_agent as model
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


model.agent.db.bind(provider='sqlite', filename=':memory:', create_db=True)
model.agent.db.generate_mapping(create_tables=True)

route = json.loads(args.route.read())
coords = [[c[0], c[1]]
          for c in route['features'][0]['geometry']['coordinates']]

start = LatLon(Latitude(coords[0][0]),
               Longitude(coords[0][1]))

end = LatLon(Latitude(coords[-1][0]),
             Longitude(coords[-1][1]))


with model.agent.orm.db_session:
    b = model.Bike()
    b.speed = args.speed
    b.random_ride(ne_lat=19.461332069967366,
                  ne_lng=-99.09204483032227,
                  sw_lat=19.40467336236742,
                  sw_lng=-99.17787551879884,
                  min_len=8, max_len=10)

    while not b.got_there():
        b.step()
        print len(b.route)
