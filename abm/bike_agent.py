from LatLon import LatLon, Latitude, Longitude
import random








    def random_ride(self, ne_lng, ne_lat, sw_lng, sw_lat):

        while True:

            a = LatLon(Latitude(random.uniform(ne_lat, sw_lat)),
                       Longitude(random.uniform(sw_lng, ne_lng)))
            c = LatLon(Latitude(random.uniform(ne_lat, sw_lat)),
                       Longitude(random.uniform(sw_lng, ne_lng)))

            # distance is in km, speed in m/s
            if a.distance(c) > 2:
                break

        self.speed = random.uniform(2, 3.5)
        self.point = (a.lon.decimal_degree,
                      a.lat.decimal_degree)
        self.destination = (c.lon.decimal_degree,
                            c.lat.decimal_degree)
        self.save()
        self.update_route(self.destination)




    def flock_with(self, bikes, heading_diff):
        """
        bikes will probably be the output of 'near' or 'within_box'.

        If the agent's heading - avg_heading is less than heading_diff
        then flock to centroid.

        Else abandon flock and head to target.

        Not implemented yet.
        """
        # compute centroid
        flock = Flock(bikes)

        # self.heading = flock.centroid

    def front_spotlight(self, diameter):
        """
        Seek other agents with similar heading
        as mine in a circle in front of me.

        Not implemented yet.
        """

        return Bike.objects(point__near=self.point,
                            point__max_distance=diameter)




class Flock:
    """
    Flock object is created from a list of agents
    and has a useful centroid
    """

    def __init__(self, bikes):
        lats = list()
        lons = list()
        for b in bikes:
            lats.append(b.point['coordinates'][0])
            lons.append(b.point['coordinates'][1])

        self.centroid = (sum(lats) / float(len(lats)),
                         sum(lons) / float(len(lons)))
