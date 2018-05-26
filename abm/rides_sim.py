import models
import argparse
import random
import pickle
import minibar
from multiprocessing.dummy import Pool as ThreadPool

parser = argparse.ArgumentParser(
    description='simulate N rides!')

parser.add_argument('--threads', default=4, type=int,
                    help='how many threads to use in pool')

parser.add_argument('--speed', default=3.0, type=float,
                    help='speed in meters per second, default=3.0')

parser.add_argument('--N', default=100, type=int,
                    help='bike population')

parser.add_argument('--steps', default=10, type=int,
                    help='simulation time steps')

parser.add_argument('--min_len', default=5.0, type=float,
                    help='minimum ride length in km')

parser.add_argument('--max_len', default=10.0, type=float,
                    help='maximum ride length in km')


parser.add_argument('--mindful', default=0.33, type=float,
                    help='probability of agents seeking to flock at each step')

parser.add_argument('--log', type=argparse.FileType('w'), required=True,
                    help='path to output pickled logfile')

args = parser.parse_args()


def new_bike(n):
    """ return new bike instance """
    b = models.Agent()
    b.speed = args.speed
    b.random_ride(ne_lat=19.461332069967366,
                  ne_lng=-99.09204483032227,
                  sw_lat=19.40467336236742,
                  sw_lng=-99.17787551879884,
                  min_len=args.min_len, max_len=args.max_len)
    b.steps_orig = len(b.route)
    return b


def ride(b):
    b.step()
    if random.random() < args.mindful:
        b.flock(all_bikes)

    return b


pool = ThreadPool(args.threads)

print "creating bikes"
all_bikes = pool.map(new_bike, range(args.N))

print "ride them home"
t = []
trips = []
for j in minibar.bar(range(args.steps)):
    all_bikes = [bk for bk in all_bikes if not bk.got_there()]

    if len(all_bikes) == 0:
        break
    else:
        t.append([len(filter(lambda b: b.status == 'solo', all_bikes)),
                  len(filter(lambda b: b.status == 'flocking', all_bikes)),
                  len(filter(lambda b: b.status == 'flocked', all_bikes))])
        all_bikes = pool.map(ride, all_bikes)

#    trips += [(bk.steps_orig,
#              bk.steps) for bk in all_bikes if bk.got_there()]


    #bike_deficit = args.N - len(all_bikes)
    #for n in range(bike_deficit):
    #    all_bikes.append(new_bike)


pickle.dump(t, args.log)

#             'trips': trips},
#            args.log)


#pool.close()
#pool.join()
