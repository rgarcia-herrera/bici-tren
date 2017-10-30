from time import sleep
from datetime import datetime
import model
# from LatLon import LatLon, Latitude, Longitude
import random


def random_within_box(sw_lat=19.37625563272936,
                      ne_lat=19.48957309227922,
                      ne_lng=-99.04912948608398,
                      sw_lng=-99.22079086303712):
    return (random.uniform(sw_lng, ne_lng),
            random.uniform(ne_lat, sw_lat))


model.connect('mydb')

# drop all bikes
for b in model.Bike.objects.all():
    b.delete()

h = 0.0
# init source, target, speed for this many bikes
for n in range(60):
    b = model.Bike()
    b.point = random_within_box()   # random start
    b.destination = random_within_box()  # random end
    b.update_route(b.destination)
    b.update(b.point)
    b.speed = random.uniform(2, 3.5)
    b.save()
    print b

while model.Bike.objects.count() > 0:
    for b in model.Bike.objects.all():
        sleep(0.05)
        print b
        if b.got_there():
            b.delete()
            break

        delta = datetime.now() - b.stamp
        if delta.seconds > 10:
            flock = model.Flock(b.get_near_bikes())

            if abs(b.heading - b.heading_to(flock.centroid)) < 0.8:
                b.update_route(flock.centroid)
        b.step()
