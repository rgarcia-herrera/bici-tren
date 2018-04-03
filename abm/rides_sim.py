import models
import argparse
from pony.orm import db_session, rollback, select, count
import random
import gzip
import csv
import pickle
from bike_stations import ecobici

parser = argparse.ArgumentParser(
    description='simulate 10,000 rides!')

parser.add_argument('--speed', default=3.0, type=float,
                    help='speed in meters per second, default=3.0')

parser.add_argument('--mindful', default=0.33, type=float,
                    help='probability of agents seeking to flock at each step')

parser.add_argument('--log', type=argparse.FileType('w'), required=True,
                    help='path to output pickled logfile')

args = parser.parse_args()


models.db.bind(provider='sqlite', filename=':memory:', create_db=True)
models.db.generate_mapping(create_tables=True)


print "load rides to db"
with gzip.open('../data/100_rides.csv.gz') as f:
    reader = csv.reader(f, delimiter=' ')
    for row in reader:
        if row[0] != row[2]:
            with db_session:
                try:
                    b = models.Agent()
                    b.speed = args.speed
                    b.set_point(ecobici[row[0]])
                    b.set_destination(ecobici[row[2]])
                    b.update_route()
                except:
                    rollback()
            print b.id


print " ride them all home"
t = []
while True:
    with db_session:
        status = select(
            (count(b.status == 'solo'),
             count(b.status == 'flocking'),
             count(b.status == 'flock')) for b in models.Agent).get()

        if sum(status) == 0:
            break
        else:
            t.append(status)

        for b in select(bike for bike in models.Agent):

            b.step()

            if b.got_there():
                b.delete()
            elif random.random() < args.mindful:
                b.flock()

pickle.dump(t, args.log)
