from time import sleep
# from datetime import datetime
import bike_agent as model
from router import refine, Router
import argparse


parser = argparse.ArgumentParser(description='grab adscriptions from medline')
parser.add_argument('--init', type=int, default=50,
                    help="set to 0 to resume run")
args = parser.parse_args()


model.connect('mydb')

if args.init > 0:
    # drop all bikes
    for b in model.Bike.objects.all():
        b.delete()

    h = 0.0
    # init source, target, speed for this many bikes
    for n in range(args.init):
        b = model.Bike()
        b.speed = 20
        b.random_ride(ne_lat=19.461332069967366,
                      ne_lng=-99.09204483032227,
                      sw_lat=19.40467336236742,
                      sw_lng=-99.17787551879884,
                      min_len=5, max_len=10)

        b.route = refine(b.route, b.speed)
        b.save()
        sleep(0.1)


def status_count():
    solo = float(model.Bike.objects(status="solo").count())
    in_flock = 0
    for b in model.Bike.objects.all():
        if b.in_flock(100):
            in_flock += 1
    # flocking = float(model.Bike.objects(status="flocking").count())
    all = float(model.Bike.objects.count())
    return {'solo': "%0.2f" % (solo / all),
            'in': "%0.2f" % (in_flock / all)}


def mean_distance():
    return sum([b.distance_to(b.destination)
                for b in model.Bike.objects.all()]) \
                    / model.Bike.objects.count()


while model.Bike.objects.count() > 0:
    for b in model.Bike.objects.all():
        if b.got_there():
            b.delete()
        else:
            b.step()
            b.reload()

        if b.get_flock_candidates(
                b.distance_to(b.destination)/2.0,
                b.distance_to(b.destination)/3.0).count() > 1:
            flock = model.Flock(
                b.get_flock_candidates(b.distance_to(b.destination)/2.0,
                                       b.distance_to(b.destination)/3.0))

            if abs(b.heading - b.heading_to(flock.centroid)) < 0.8:
                if b.status == "solo":
                    router = Router(points=[b.point['coordinates'],
                                            flock.centroid,
                                            b.destination['coordinates']])

                    b.route = refine(router.route, b.speed)
                    b.status = 'flocking'
                    b.speed = 30
                    b.save()
            else:
                if not b.in_flock(100):
                    router = Router(points=[b.point['coordinates'],
                                            b.destination['coordinates']])
                    b.route = refine(router.route, b.speed)
                    b.status = "solo"
                    b.speed = 20
                else:
                    b.speed = flock.mean_speed
                b.save()

    print status_count(), mean_distance()
