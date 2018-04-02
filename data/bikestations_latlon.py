import json
import gzip
from pprint import pprint

with gzip.open('cicloestaciones.json.gz') as f:
    stations = json.load(f)

    for s in stations['stations']:
        print "'%s' : LatLon(Latitude(%s), Longitude(%s))," % (s['id'], s['location']['lat'], s['location']['lon'])
