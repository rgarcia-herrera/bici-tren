from time import sleep
from pony.orm import db_session, Database
import model
import argparse
import json
import urllib2

parser = argparse.ArgumentParser(
    description='update bike agent')

parser.add_argument('--id', type=int, default=1,
                    help='bike id')

args = parser.parse_args()

model.db.bind('sqlite', 'bikes.sqlite', create_db=False)
model.db.generate_mapping(create_tables=False)

route_url = "http://h2096617.stratoserver.net:443/brouter?lonlats=%s,%s|%s,%s&profile=trekking&alternativeidx=0&format=geojson"
route = json.loads(urllib2.urlopen(route_url % (-99.133,
                                                19.431,
                                                -99.137,
                                                19.435)).read())
coords = route['features'][0]['geometry']['coordinates']


while True:

    for lonlat in coords:
        with db_session:    
            b = model.Bike[args.id]
            b.lon = lonlat[0]
            b.lat = lonlat[1]
            print b
        sleep(1.5)
        
