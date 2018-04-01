import bike_agent as model
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


model.agent.db.bind(provider='sqlite', filename='db.sqlite', create_db=True)
model.agent.db.generate_mapping(create_tables=True)


@db_session
def random_ride(bike, ne_lng, ne_lat, sw_lng, sw_lat,
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
            bike.set_point(a)
            bike.set_destination(c)

            if bike.update_route():
                break


with model.agent.orm.db_session:
    b = model.Bike[1]
    b.speed = args.speed
    random_ride(bike=b,
                ne_lat=19.461332069967366,
                ne_lng=-99.09204483032227,
                sw_lat=19.40467336236742,
                sw_lng=-99.17787551879884,
                min_len=8, max_len=10)
    commit()

while not b.got_there():
    with model.agent.orm.db_session:
        b = model.Bike[1]
        b.step()
    print len(b.route)
    sleep(0.1)
