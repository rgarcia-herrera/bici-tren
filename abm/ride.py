import models
import argparse
from LatLon import LatLon, Latitude, Longitude
from time import sleep
from pony.orm import db_session, commit
import random

parser = argparse.ArgumentParser(
    description='ride bike at speed thru route')

parser.add_argument('--speed', default=3.0, type=float,
                    help='speed in meters per second, default=3.0')

args = parser.parse_args()


models.db.bind(provider='sqlite', filename=':memory:', create_db=True)
models.db.generate_mapping(create_tables=True)


@db_session
def random_ride(agent, ne_lng, ne_lat, sw_lng, sw_lat,
                min_len=2, max_len=10):
    """
    params are bounding box and minimum length in kilometres
    """
    while True:

        a = LatLon(Latitude(random.uniform(ne_lat, sw_lat)),
                   Longitude(random.uniform(sw_lng, ne_lng)))
        c = LatLon(Latitude(random.uniform(ne_lat, sw_lat)),
                   Longitude(random.uniform(sw_lng, ne_lng)))

        if a.distance(c) >= min_len and a.distance(c) <= max_len:
            agent.set_point(a)
            agent.set_destination(c)

            if agent.update_route():
                break


with db_session:
    b0 = models.Agent()
    b1 = models.Agent()
    commit()

    id0 = b0.id
    id1 = b1.id
    print id1, id0

with db_session:
    b = models.Agent[id0]
    b.speed = args.speed
    random_ride(agent=b,
                ne_lat=19.461332069967366,
                ne_lng=-99.09204483032227,
                sw_lat=19.40467336236742,
                sw_lng=-99.17787551879884,
                min_len=8, max_len=10)

    b1 = models.Agent[id1]
    b1.speed = args.speed
    s = LatLon(Latitude(b.lat - 0.0021),
               Longitude(b.lon + 0.0041))
    t = LatLon(Latitude(b.dest_lat + 0.0081),
               Longitude(b.dest_lon - 0.0081))

    b1.set_point(s)
    b1.set_destination(t)
    b1.update_route()

while not b.got_there():
    with db_session:
        b = models.Agent[id0]
        b1 = models.Agent[id1]
        b.step()
        b1.step()
        if random.choice([True, False, False]):
            b.flock()
        if random.choice([True, False, False]):
            b1.flock()

        print b.status, len(b.route), b1.status, \
            len(b1.route), b.point().distance(b1.point())
