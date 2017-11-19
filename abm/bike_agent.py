import json
import urllib2
import random


def split(s, t, speed):
    """
    returns points between s(ource) and t(arget) at intervals of size @speed
    """
    s = LatLon(Latitude(s[1]),
               Longitude(s[0]))

    t = LatLon(Latitude(t[1]),
               Longitude(t[0]))

    heading = s.heading_initial(t)

    fine = [(s.lon.decimal_degree,
             s.lat.decimal_degree), ]
    wp = s

    while True:
        dst = wp.offset(heading,
                        speed / 1000.0)

        if dst.distance(t) * 1000.0 > speed:
            fine.append((dst.lon.decimal_degree,
                         dst.lat.decimal_degree))
            wp = dst
        else:
            fine.append((t.lon.decimal_degree,
                         t.lat.decimal_degree))
            break

    return fine


def refine(route, speed):
    """
    returns a finer-grain route, splitting it at @speed intervals
    """
    assert len(route) > 1
    fine = [route[0], ]
    for i in range(len(route)-1):
        fine += split(route[i], route[i + 1], speed)[1:-1]
    fine.append(route[-1])
    return fine


def update_route(self, point):
        """
        Use local instance of brouter to get route to point
        """
        self.reload()
        host = "localhost:17777"
        route_url = "http://{host}/brouter?lonlats={source}|{target}" \
                    + "&profile=trekking&alternativeidx=0&format=geojson"

        source = self.point['coordinates']

        if 'coordinates' in point:
            target = point['coordinates']
        else:
            target = point

        response = urllib2.urlopen(
                route_url.format(
                    host=host,
                    source=",".join([str(x)
                                     for x in
                                     source]),
                    target=",".join([str(x)
                                     for x in target])))
        broute_json = response.read()

        try:
            self.set_route_from_geojson(broute_json)
        except ValueError:
            print "bronca leyendo el json", broute_json
            self.route = None

    def set_route_from_geojson(self, geojson):
        route = json.loads(geojson)
        self.route = [(c[0], c[1])
                      for c in route['features'][
                              0]['geometry']['coordinates']]






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
