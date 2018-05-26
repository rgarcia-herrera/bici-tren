import argparse
import random
import pickle
import minibar
from multiprocessing.dummy import Pool as ThreadPool

parser = argparse.ArgumentParser(
    description='simulate N rides!')

parser.add_argument('--threads', default=4, type=int,
                    help='how many threads to use in pool')

parser.add_argument('--steps', default=10, type=int,
                    help='simulation time steps')

parser.add_argument('--mindful', default=0.33, type=float,
                    help='probability of agents seeking to flock at each step')

parser.add_argument('--log', type=argparse.FileType('w'), required=True,
                    help='path to output pickled logfile')

parser.add_argument('--bikes', type=argparse.FileType('r'), required=True,
                    help='path to pickled lit of agents')


args = parser.parse_args()


def ride(b):
    b.step()
    if random.random() < args.mindful:
        b.flock(all_bikes)

    return b


pool = ThreadPool(args.threads)

print "loading bikes"
all_bikes = pickle.load(args.bikes)

print "ride them home"
t = []
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
