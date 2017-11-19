from time import sleep
from datetime import datetime
import bike_agent as model

model.connect('mydb')

# drop all bikes
for b in model.Bike.objects.all():
    b.delete()

h = 0.0
# init source, target, speed for this many bikes
for n in range(1):
    b = model.Bike()
    b.random_ride(sw_lat=19.37625563272936,
                  ne_lat=19.48957309227922,
                  ne_lng=-99.04912948608398,
                  sw_lng=-99.22079086303712)
    sleep(1)
    print "creada %s" % b

while model.Bike.objects.count() > 0:
    for b in model.Bike.objects.all():
        delta = datetime.now() - b.stamp
        if delta.seconds > 10:
            if b.get_near_bikes(10000).count() > 1:
                flock = model.Flock(b.get_near_bikes(1000))

                if abs(b.heading - b.heading_to(flock.centroid)) < 0.8:
                    b.update_route(flock.centroid)
                    b.status = 'flocking'

        b.step()
        print b

        if b.got_there():
            b.delete()

        sleep(0.5)
