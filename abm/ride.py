import bike_agent as model
import argparse
import json
from LatLon import LatLon, Latitude, Longitude
from time import sleep
from pony.orm import commit


parser = argparse.ArgumentParser(
    description='ride bike at speed thru route')

parser.add_argument('--speed', default=3.0, type=float,
                    help='speed in meters per second, default=3.0')

args = parser.parse_args()


model.agent.db.bind(provider='sqlite', filename='db.sqlite', create_db=True)
model.agent.db.generate_mapping(create_tables=True)

with model.agent.orm.db_session:
    b = model.Bike[1]
    b.speed = args.speed
    b.random_ride(ne_lat=19.461332069967366,
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
