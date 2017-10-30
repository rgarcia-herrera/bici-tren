from mongoengine import Document, FloatField, \
    DateTimeField, PointField, LineStringField, \
    connect  # must import connect, used from without
from datetime import datetime
import utm
from util import swap_coords
import svgwrite
from LatLon import LatLon, Latitude, Longitude
import json
import urllib2


class Flock:

    def __init__(self, bikes):
        lats = list()
        lons = list()
        for b in bikes:
            lats.append(b.point[0])
            lons.append(b.point[1])

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
        return "<bike %s %s @%sm/s>" % (self.id, self.point, self.speed)

    def get_point_xy(self):
        return utm.from_latlon(*swap_coords(self.point))

    def get_destination_xy(self):
        return utm.from_latlon(*swap_coords(self.destination))

    def set_xy(self, x, y, ZONE_NUMBER, ZONE_LETTER):
        new_point = swap_coords(utm.to_latlon(x, y, ZONE_NUMBER, ZONE_LETTER))
        self.update(new_point)

    def update(self, new_point):
        a = LatLon(Longitude(self.point[1]),
                   Latitude(self.point[0]))

        b = LatLon(Longitude(new_point[1]),
                   Latitude(new_point[0]))

        c = LatLon(Longitude(self.destination[1]),
                   Latitude(self.destination[0]))

        self.heading = a.heading_initial(b)
        self.destination_heading = b.heading_initial(c)

        tdelta = datetime.now() - self.stamp
        seconds = tdelta.total_seconds()
        distance = a.distance(b) / 1000.0
        self.speed = distance / seconds

        self.stamp = datetime.now()
        self.point = new_point

    def heading_to(self, other_point):
        a = LatLon(Longitude(self.point[1]),
                   Latitude(self.point[0]))

        b = LatLon(Longitude(other_point[1]),
                   Latitude(other_point[0]))

        return a.heading_initial(b)

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
        s = LatLon(Latitude(self.point['coordinates'][1]),
                   Longitude(self.point['coordinates'][0]))
        t = LatLon(Latitude(self.destination['coordinates'][1]),
                   Longitude(self.destination['coordinates'][0]))
        if s.distance(t) < self.speed:
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

    def speed_waypoints(self, coords):
        for i in range(1, len(coords)):
            a = LatLon(Latitude(self.point[1]),
                       Longitude(self.point[0]))
            c = LatLon(Latitude(coords[i][1]),
                       Longitude(coords[i][0]))
            # distance is in km, speed in m/s
            while a.distance(c) > self.speed / 1000.0:
                dst = a.offset(a.heading_initial(c),
                               self.speed)
                yield [dst.lon.decimal_degree,
                       dst.lat.decimal_degree]
                a = LatLon(Latitude(self.point[1]),
                           Longitude(self.point[0]))
                c = LatLon(Latitude(coords[i][1]),
                           Longitude(coords[i][0]))

            print "reached waypoint %s" % c
            yield [coords[i][0],
                   coords[i][1]]

    def update_route(self, point):

        """
        Use local instance of brouter to get route to point
        """
        host = "http://localhost:17777"
        route_url = "http://{host}/brouter?lonlats={source}|{target}" \
                    + "&profile=trekking&alternativeidx=0&format=geojson"

        route = json.loads(
            urllib2.urlopen(
                route_url.format(host=host,
                                 source=self.point,
                                 target=point)).read())
        self.route = route

    def step(self):
        p = self.speed_waypoints(self.route).next()
        self.update(p)
