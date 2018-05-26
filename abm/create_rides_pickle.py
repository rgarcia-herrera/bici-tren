import models
import argparse
import pickle
from multiprocessing.dummy import Pool as ThreadPool

parser = argparse.ArgumentParser(
    description='create N agents, pickle them')

parser.add_argument('--N', default=100, type=int,
                    help='bike population')

parser.add_argument('--min_len', default=5.0, type=float,
                    help='minimum ride length in km')

parser.add_argument('--max_len', default=10.0, type=float,
                    help='maximum ride length in km')

parser.add_argument('--pickle', type=argparse.FileType('w'), required=True,
                    help='path to output pickled list of agents')

parser.add_argument('--speed', default=3.0, type=float,
                    help='speed in meters per second, default=3.0')

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


pool = ThreadPool(4)

print "creating bikes"
all_bikes = pool.map(new_bike, range(args.N))

pickle.dump(all_bikes, args.pickle)
