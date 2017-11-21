from mongoengine import connect  # must import connect, used from without
from agent import Agent
from LatLon import LatLon, Latitude, Longitude
import random
from router import Router


class Flock:
    """
    Flock object is created from a list of agents
    and has a useful centroid
    """

    def __init__(self, bikes):
        lats = list()
        lons = list()
        speeds = []
        for b in bikes:
            speeds.append(b.speed)
            lats.append(b.point['coordinates'][0])
            lons.append(b.point['coordinates'][1])

        self.mean_speed = sum(speeds) / float(len(speeds))
        self.centroid = (sum(lats) / float(len(lats)),
                         sum(lons) / float(len(lons)))


class Bike(Agent):

    def random_ride(self, ne_lng, ne_lat, sw_lng, sw_lat,
                    min_len=2, max_len=10):
        """
        params are bounding box and minimum length in kilometres
        """
        print "seeking random route"
        while True:

            a = LatLon(Latitude(random.uniform(ne_lat, sw_lat)),
                       Longitude(random.uniform(sw_lng, ne_lng)))
            c = LatLon(Latitude(random.uniform(ne_lat, sw_lat)),
                       Longitude(random.uniform(sw_lng, ne_lng)))

            if a.distance(c) >= min_len and a.distance(c) <= max_len:
                self.point = (a.lon.decimal_degree,
                              a.lat.decimal_degree)
                self.destination = (c.lon.decimal_degree,
                                    c.lat.decimal_degree)

                router = Router(points=[self.point,
                                        self.destination])
                if router.route:
                    self.route = router.route
                    self.save()
                    break

    def get_flock_candidates(self, rpoint, rdest):
        return Agent.objects(point__near=self.point,
                             point__max_distance=rpoint,
                             destination__near=self.destination,
                             destination__max_distance=rdest)

    # def flock_with(self, bikes, heading_diff):
    #     """
    #     bikes will probably be the output of 'near' or 'within_box'.

    #     If the agent's heading - avg_heading is less than heading_diff
    #     then flock to centroid.

    #     Else abandon flock and head to target.

    #     Not implemented yet.
    #     """
    #     # compute centroid
    #     flock = Flock(bikes)

    #     # self.heading = flock.centroid

    # def front_spotlight(self, diameter):
    #     """
    #     Seek other agents with similar heading
    #     as mine in a circle in front of me.

    #     Not implemented yet.
    #     """

    #     return Bike.objects(point__near=self.point,
    #                         point__max_distance=diameter)
