from time import sleep
import model
import argparse
import json
import urllib2
from random import uniform

parser = argparse.ArgumentParser(
    description='update bike agent')

parser.add_argument('--id', required=True,
                    help='bike id')

args = parser.parse_args()

model.connect('mydb')

route_url = "http://toho.mine.nu/brouter/brouter?lonlats=%s,%s|%s,%s&profile=trekking&alternativeidx=0&format=geojson"

while True:
    try:
        route = json.loads(
            urllib2.urlopen(route_url % (uniform(-99.1, -99.0),
                                         uniform(19.2, 19.5),
                                         uniform(-99.1, -99.0),
                                         uniform(19.4, 19.5))).read())
        coords = route['features'][0]['geometry']['coordinates']
    except:
        pass

    b = model.Bike.objects.with_id(args.id)
    for lonlat in coords:
        b.point = (lonlat[1], lonlat[0])
        b.save()
        print b
        sleep(1.5)
