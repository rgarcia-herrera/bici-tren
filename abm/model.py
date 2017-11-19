from mongoengine import Document, FloatField, \
    DateTimeField, PointField, LineStringField, \
    StringField, connect  # must import connect, used from without
from datetime import datetime
import utm
from util import swap_coords
import svgwrite
from LatLon import LatLon, Latitude, Longitude
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
    assert len(route) > 1
    fine = [route[0], ]
    for i in range(len(route)-1):
        fine += split(route[i], route[i + 1], speed)[1:-1]
    fine.append(route[-1])
    return fine


class Flock:

    def __init__(self, bikes):
        lats = list()
        lons = list()
        for b in bikes:
            lats.append(b.point['coordinates'][0])
            lons.append(b.point['coordinates'][1])

        self.centroid = (sum(lats) / float(len(lats)),
                         sum(lons) / float(len(lons)))


class Bike(Document):
    point = PointField()
    speed = FloatField(default=0)
    heading = FloatField(default=0)
    destination_heading = FloatField(default=0)
    destination = PointField(required=False)
    stamp = DateTimeField(default=datetime.now)
    route = LineStringField()
    # route_flock = LineStringField()

    # status = StringField()

    def point_as_LatLon(self):
        return LatLon(Longitude(self.point['coordinates'][1]),
                      Latitude(self.point['coordinates'][0]))

    def to_dict(self):
        return {'bike_id': "%s" % self.id,
                'point': self.point,
                'speed': self.speed,
                'heading': float("%0.2f" %
                                 self.heading),
                'destination_heading': float("%0.2f" %
                                             self.destination_heading),
                'destination': self.destination,
                'stamp': str(self.stamp)}

    def __str__(self):
        return "<bike %s %s away @%sm/s>" % (self.id, self.distance_to(self.destination), self.speed)

    def get_point_xy(self):
        return utm.from_latlon(*swap_coords(self.point))

    def get_destination_xy(self):
        return utm.from_latlon(*swap_coords(self.destination))

    def set_xy(self, x, y, ZONE_NUMBER, ZONE_LETTER):
        new_point = swap_coords(utm.to_latlon(x, y, ZONE_NUMBER, ZONE_LETTER))
        self.update(new_point)

    def update(self, new_point):

        if 'coordinates' in self.point:
            a = LatLon(Longitude(self.point['coordinates'][1]),
                       Latitude(self.point['coordinates'][0]))
        else:
            a = LatLon(Longitude(self.point[1]),
                       Latitude(self.point[0]))

        b = LatLon(Longitude(new_point[1]),
                   Latitude(new_point[0]))

        if 'coordinates' in self.destination:
            c = LatLon(Longitude(self.destination['coordinates'][1]),
                       Latitude(self.destination['coordinates'][0]))
        else:
            c = LatLon(Longitude(self.destination[1]),
                       Latitude(self.destination[0]))

        self.heading = a.heading_initial(b)
        self.destination_heading = b.heading_initial(c)

        # tdelta = datetime.now() - self.stamp
        # seconds = tdelta.total_seconds()
        # distance = a.distance(b) / 1000.0
        # self.speed = distance / seconds

        self.stamp = datetime.now()
        self.point = new_point
        self.save()
        self.reload()

    def heading_to(self, other_point):
        a = LatLon(Longitude(self.point['coordinates'][1]),
                   Latitude(self.point['coordinates'][0]))

        b = LatLon(Longitude(other_point[1]),
                   Latitude(other_point[0]))

        return a.heading_initial(b)

    def distance_to(self, other_point):
        """
        distance from bike to another point, in metres
        """
        if 'coordinates' in self.point:
            s = LatLon(Latitude(self.point['coordinates'][1]),
                       Longitude(self.point['coordinates'][0]))
        else:
            s = LatLon(Latitude(self.point[1]),
                       Longitude(self.point[0]))

        if 'coordinates' in other_point:
            t = LatLon(Latitude(other_point['coordinates'][1]),
                       Longitude(other_point['coordinates'][0]))
        else:
            t = LatLon(Latitude(other_point[1]),
                       Longitude(other_point[0]))

        return s.distance(t) * 1000.0

    def marker(self):
        dwg = svgwrite.Drawing()
        dwg.viewbox(width=100, height=100)
        dh = svgwrite.shapes.Polygon(points=[[50, 20],
                                             [30, 80],
                                             [70, 80]],
                                     fill='blue', opacity=0.6)
        dh.rotate(self.destination_heading,
                  center=(50, 50))

        h = svgwrite.shapes.Polygon(points=[[50, 30],
                                            [35, 75],
                                            [65, 75]],
                                    fill='yellow',
                                    opacity=0.44,
                                    stroke="green",
                                    stroke_width=1,
                                    stroke_opacity=1)
        h.rotate(self.heading,
                 center=(50, 50))
        dwg.add(dh)
        dwg.add(h)

        return dwg.tostring()

    def get_near_bikes(self, radius):
        return Bike.objects(point__near=self.point,
                            point__max_distance=radius)  # incluir heading aca?

    def got_there(self):
        if self.distance_to(self.destination) < self.speed:
            return True
        else:
            return False

    def flock_with(self, bikes, heading_diff):
        """
        bikes will probably be the output of 'near' or 'within_box'.

        If the agent's heading - avg_heading is less than heading_diff
        then flock to centroid.

        Else abandon flock and head to target.
        """
        # compute centroid
        flock = Flock(bikes)

        self.heading = flock.centroid

    def front_spotlight(self, diameter):
        """
        Seek other agents with similar heading
        as mine in a circle in front of me.

        Not implemented yet.
        """

        return Bike.objects(point__near=self.point,
                            point__max_distance=diameter)

    def speed_waypoints(self, route):

        for i in range(1, len(route['coordinates'])):
            while True:
                a = LatLon(Latitude(self.point['coordinates'][1]),
                           Longitude(self.point['coordinates'][0]))
                c = LatLon(Latitude(route['coordinates'][i][1]),
                           Longitude(route['coordinates'][i][0]))

                dst = a.offset(a.heading_initial(c),
                               self.speed)

                # distance is in km, speed in m/s
                if a.distance(c) * 1000.0 - self.speed * 2 > 30:
#                    print "faltan %s m" % float(a.distance(c)) * 1000
                    yield [dst.lon.decimal_degree,
                           dst.lat.decimal_degree]
                else:
                    print "reached waypoint %s" % c
                    yield [route['coordinates'][i][0],
                           route['coordinates'][i][1]]
                    break

    def towards(self, point_b):

        a = self.point_as_LatLon()
        b = LatLon(Latitude(point_b[1]),
                   Longitude(point_b[0]))

        dst = a.offset(a.heading_initial(b),
                       self.speed)

        # distance is in km, speed in m/s
        if (a.distance(b) * 1000.0) - (self.speed * 2) > 30:
            #                    print "faltan %s m" % float(a.distance(c)) * 1000
            return [dst.lon.decimal_degree,
                    dst.lat.decimal_degree], False
        else:
            print "reached point b"
            return point_b, True

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

    def step(self):
        self.reload()
        p, got_there = self.towards(self.route['coordinates'][0])
        if not got_there:
            print "hacia el primer punto"
            self.update(p)
        else:
            print "actualizar ruta"
            self.update_route(self.destination)

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
