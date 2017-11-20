from time import sleep
# from datetime import datetime
import bike_agent as model
from router import refine

model.connect('mydb')

# drop all bikes
for b in model.Bike.objects.all():
    b.delete()

h = 0.0
# init source, target, speed for this many bikes
for n in range(50):
    b = model.Bike()
    b.speed = 30
    b.random_ride(ne_lat=19.450649369224482,
                  ne_lng=-99.11805152893068,
                  sw_lat=19.422320621845056,
                  sw_lng=-99.16096687316896,
                  min_len=1, max_len=4)
    b.route = refine(b.route, 15)
    b.save()
    sleep(0.3)
    print "creada %s" % b

while model.Bike.objects.count() > 0:
    for b in model.Bike.objects.all():
        if b.got_there():
            b.delete()
        else:
            b.step()
            print b
        # if b.get_near_bikes(10000).count() > 1:
        #     flock = model.Flock(b.get_near_bikes(1000))

        #     if abs(b.heading - b.heading_to(flock.centroid)) < 0.8:
        #         b.update_route(flock.centroid)
        #         b.status = 'flocking'

    sleep(0.1)
