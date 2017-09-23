from mongoengine import Document, FloatField, \
    DateTimeField, PointField, LineStringField, \
    connect  # must import connect, used from without
from datetime import datetime
from math import atan, degrees
import utm
from util import distance, swap_coords
import svgwrite
from random import randint
from LatLon import LatLon, Latitude, Longitude


class Bike(Document):
    point = PointField()
    speed = FloatField(default=0)
    heading = FloatField(default=0)
    destination_heading = FloatField(default=0)
    destination = PointField(required=False)
    stamp = DateTimeField(default=datetime.now)

    def to_dict(self):
        return {'point': self.point,
                'speed': self.speed,
                'heading': self.heading,
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
        
        # tdelta = datetime.now() - self.stamp
        # seconds = tdelta.total_seconds()
        # self.speed = distance(x1, y1, x2, y2) / seconds

        self.stamp = datetime.now()
        self.point = new_point

    def marker(self, color='red'):
        dwg = svgwrite.Drawing()
        dwg.viewbox(width=100, height=100)
        p = svgwrite.shapes.Polygon(points=[[50, 20],
                                            [30, 80],
                                            [70, 80]],
                                    fill=color, opacity=0.9)
        p.rotate(self.destination_heading,
                 center=(50, 50))
        dwg.add(p)
        return dwg.tostring()
