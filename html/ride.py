from time import sleep
import model
import argparse
import json
from LatLon import LatLon, Latitude, Longitude

parser = argparse.ArgumentParser(
    description='ride bike at speed thru route')

parser.add_argument('--geojson', type=argparse.FileType('r'), required=True,
                    help='A BRouter route in geojson format.')
parser.add_argument('--speed', default=3.0, type=float,
                    help='speed in meters per second, default=3.0')
parser.add_argument('--id', default='new',
                    help='bike id')

args = parser.parse_args()
model.connect('mydb')
route = json.loads(args.geojson.read())

coords = [[c[0], c[1]]
          for c in route['features'][0]['geometry']['coordinates']]

start = [coords[0][0],
         coords[0][1]]

end = [coords[-1][0],
       coords[-1][1]]

if args.id == 'new':
    b = model.Bike()
else:
    b = model.Bike.objects.with_id(args.id)

b.point = start
b.destination = end
b.speed = args.speed
b.save()

print "riding:", b


def waypoints(coords, step):
    for i in range(1, len(coords)):
        a = LatLon(Latitude(b.point[1]),
                   Longitude(b.point[0]))
        c = LatLon(Latitude(coords[i][1]),
                   Longitude(coords[i][0]))
        if a.distance(c) <= step:
            print "reached waypoint %s" % c
            yield [coords[i][0],
                   coords[i][1]]
        else:
            dst = a.offset(a.heading_initial(c), step)
            yield [dst.lon.decimal_degree,
                   dst.lat.decimal_degree]


for p in waypoints(coords, args.speed / 1000.0):
    b.update(p)
    b.save()
    print b
    sleep(1)
