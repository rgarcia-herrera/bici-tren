import models
import argparse
import random
import gzip
import csv
import pickle
import time
from bike_stations import ecobici
import minibar

parser = argparse.ArgumentParser(
    description='simulate 10,000 rides!')

parser.add_argument('--speed', default=3.0, type=float,
                    help='speed in meters per second, default=3.0')

parser.add_argument('--N', default=100, type=int,
                    help='bike population')

parser.add_argument('--steps', default=10, type=int,
                    help='simulation time steps')

parser.add_argument('--min_len', default=8.33, type=float,
                    help='minimum ride length in km')

parser.add_argument('--max_len', default=10.33, type=float,
                    help='maximum ride length in km')


parser.add_argument('--mindful', default=0.33, type=float,
                    help='probability of agents seeking to flock at each step')

parser.add_argument('--log', type=argparse.FileType('w'), required=True,
                    help='path to output pickled logfile')

args = parser.parse_args()


print "creating bikes"
rides = {}
all_bikes = []
for j in minibar.bar(range(args.N)):
    b = models.Agent()
    b.speed = args.speed
    b.random_ride(ne_lat=19.461332069967366,
                  ne_lng=-99.09204483032227,
                  sw_lat=19.40467336236742,
                  sw_lng=-99.17787551879884,
                  min_len=args.min_len, max_len=args.max_len)
    all_bikes.append(b)
    rides[id(b)] = {'steps_orig': len(b.route),
                    'steps_given': 0,
                    'got_there': False}

print
print "ride them home"

t = []
for j in minibar.bar(range(args.steps)):
    solo = len(filter(lambda b: b.status == 'solo', all_bikes))
    flocking = len(filter(lambda b: b.status == 'flocking', all_bikes))
    flock = len(filter(lambda b: b.status == 'flock', all_bikes))
    t.append([solo, flocking, flock])

    for b in all_bikes:
        rides[id(b)]['steps_given'] = b.steps

        if b.got_there():
            rides[id(b)]['got_there'] = True
            all_bikes.remove(b)

            b = models.Agent()
            b.speed = args.speed
            b.random_ride(ne_lat=19.461332069967366,
                          ne_lng=-99.09204483032227,
                          sw_lat=19.40467336236742,
                          sw_lng=-99.17787551879884,
                          min_len=args.min_len, max_len=args.max_len)
            all_bikes.append(b)
            rides[id(b)] = {'direct': len(b.route),
                            'flocking': 0,
                            'got_there': False}
        else:
            b.step()
            if random.random() < args.mindful:
                b.flock(all_bikes)

pickle.dump({'t':t,
             'rides': rides},
            args.log)
