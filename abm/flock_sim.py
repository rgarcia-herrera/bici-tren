from time import sleep
# from datetime import datetime
import bike_agent as model
from router import refine, Router

model.connect('mydb')

# drop all bikes
for b in model.Bike.objects.all():
    b.delete()

h = 0.0
# init source, target, speed for this many bikes
for n in range(100):
    b = model.Bike()
    b.speed = 30
    b.random_ride(ne_lat=19.461332069967366,
                  ne_lng=-99.09204483032227,
                  sw_lat=19.40467336236742,
                  sw_lng=-99.17787551879884,
                  min_len=5, max_len=10)

    b.route = refine(b.route, b.speed)
    b.save()
    sleep(0.1)
    print "creada %s" % b


def status_count():
    solo = float(model.Bike.objects(status="solo").count())
    flocking = float(model.Bike.objects(status="flocking").count())
    all = float(model.Bike.objects.count())
    return {'solo': "%0.2f" % (solo / all),
            'flocking': flocking / all}


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
                    b.save()
            else:
                if b.status == 'flocking':
                    router = Router(points=[b.point['coordinates'],
                                            b.destination['coordinates']])
                    b.route = refine(router.route, b.speed)
                    b.status = "solo"
                    b.save()

    print status_count(), mean_distance()
