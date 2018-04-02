import models
import argparse
from pony.orm import db_session, commit, select, count
import random
import gzip
import csv
from bike_stations import ecobici

parser = argparse.ArgumentParser(
    description='simulate 10,000 rides!')

parser.add_argument('--speed', default=3.0, type=float,
                    help='speed in meters per second, default=3.0')

parser.add_argument('--mindful', default=0.33, type=float,
                    help='probability of agents seeking to flock at each step')

args = parser.parse_args()


models.db.bind(provider='sqlite', filename=':memory:', create_db=True)
models.db.generate_mapping(create_tables=True)


# load rides to db
with db_session:
    with gzip.open('../data/1k_rides.csv.gz') as f:
        reader = csv.reader(f, delimiter=' ')
        for row in reader:
            b = models.Agent()
            b.speed = args.speed
            b.set_point(ecobici[row[0]])
            b.set_destination(ecobici[row[2]])
            b.update_route()

            commit()


# ride them all home
t = 0
while True:
    with db_session:
        if count(bike for bike in models.Agent) == 0:
            break

        for b in select(bike for bike in models.Agent):
            print b.id, t, b.status

            b.step()

            if b.got_there():
                b.delete()
            elif random.random() < args.mindful:
                b.flock()

        t += 1
