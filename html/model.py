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
from time import sleep


class Bike(Document):
    point = PointField()
    speed = FloatField(default=0)
    heading = FloatField(default=0)
    destination_heading = FloatField(default=0)
    destination = PointField(required=False)
    stamp = DateTimeField(default=datetime.now)

    def to_dict(self):
        return {'bike_id': "%s" % self.id,
                'point': self.point,
                'speed': self.speed,
                'heading': self.heading,
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

    def get_near_bikes(self):
        return Bike.objects(point__near=self.point,
                            point__max_distance=1000,
                            destination__near=self.destination,
                            destination__max_distance=500)

    def flock_with(self, bikes, heading_diff):
        """
        bikes will probably be the output of 'near' or 'within_box'.

        If the agent's heading - avg_heading is less than heading_diff
        then flock to centroid.

        Else abandon flock and head to target.
        """
        bikes = Bike.objects(point__near=self.point,
                             point__max_distance=1000,
                             destination__near=self.destination,
                             destination__max_distance=500)

        all_headings = [b.heading for b in bikes]

        flock_heading = sum(all_headings) / len(all_headings)

        # compute centroid
        centroid = 3

        if self.heading - flock_heading < heading_diff:
            self.heading = centroid

    def front_spotlight(self, diameter):
        """
        Seek other agents with similar heading
        as mine in a circle in front of me
        """

        return Bike.objects(point__near=self.point,
                            point__max_distance=1000,
                            destination__near=self.destination,
                            destination__max_distance=500)

    def next_waypoint(self, coords, step):
        for i in range(1, len(coords)):
            a = LatLon(Latitude(self.point[1]),
                       Longitude(self.point[0]))
            c = LatLon(Latitude(coords[i][1]),
                       Longitude(coords[i][0]))
            while a.distance(c) > step:
                dst = a.offset(a.heading_initial(c), step)
                yield [dst.lon.decimal_degree,
                       dst.lat.decimal_degree]
                a = LatLon(Latitude(self.point[1]),
                           Longitude(self.point[0]))
                c = LatLon(Latitude(coords[i][1]),
                           Longitude(coords[i][0]))

            print "reached waypoint %s" % c
            yield [coords[i][0],
                   coords[i][1]]

    def route_to(self, point):

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
        return route

    def ride_to(self, point):
        for p in self.next_waypoint(self.route_to(point),
                                    self.speed / 1000.0):
            self.update(p)
            self.save()
            print self
            sleep(1)
