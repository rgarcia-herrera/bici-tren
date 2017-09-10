from time import sleep
from pony.orm import db_session, Database
import model
import argparse
import json
import urllib2
from random import uniform

parser = argparse.ArgumentParser(
    description='update bike agent')

parser.add_argument('--id', type=int, default=1,
                    help='bike id')

args = parser.parse_args()

model.db.bind('sqlite', 'bikes.sqlite', create_db=False)
model.db.generate_mapping(create_tables=False)

route_url = "http://toho.mine.nu/brouter/brouter?lonlats=%s,%s|%s,%s&profile=trekking&alternativeidx=0&format=geojson"
#/brouter?lonlats=-99.166718,19.407345|-99.09256,19.476627&nogos=&profile=trekking&alternativeidx=0&format=geojson



while True:
    try:
        route = json.loads(urllib2.urlopen(route_url % (uniform(-99.1, -99.0),
                                                    uniform(19.2, 19.5),
                                                    uniform(-99.1, -99.0),
                                                    uniform(19.4, 19.5))).read())
        coords = route['features'][0]['geometry']['coordinates']
    except:
        pass
    
    for lonlat in coords:
        with db_session:    
            b = model.Bike[args.id]
            b.lon = lonlat[0]
            b.lat = lonlat[1]
            print b
        sleep(1.5)
        
