from time import sleep
import model
import argparse
import json
import matplotlib.pyplot as plt
import utm
from util import segment

from pprint import pprint

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


coords = route['features'][0]['geometry']['coordinates']

xycoords = []
for c in coords:
    (x, y,
     ZONE_NUMBER,
     ZONE_LETTER) = utm.from_latlon(c[1],
                                    c[0])

    xycoords.append([x, y])

wp = []
for i in range(1, len(xycoords)):
    a = xycoords[i-1]
    b = xycoords[i]
    wp += segment(a, b, args.speed)


waypoints = sorted(xycoords + wp)
pprint(waypoints)
plt.plot([p[0] for p in waypoints],
         [p[1] for p in waypoints], 'o')
plt.axis('equal')
plt.show()

start = [coords[0][0],
         coords[0][1]]

end = [coords[-1][0],
       coords[-1][1]]

if args.id == 'new':
    b = model.Bike(point=start,
                   destination=end,
                   speed=args.speed)
    b.save()
else:
    b = model.Bike.objects.with_id(args.id)
    b.point = start
    b.destination = end
    b.speed = args.speed
    b.save()

print "riding:", b

for p in waypoints:
    b.set_xy(p[0], p[1], ZONE_NUMBER, ZONE_LETTER)
    b.save()
    print b
    sleep(1)
