from mongoengine import Document, FloatField, \
    DateTimeField, PointField, LineStringField, \
    connect  # must import connect, used from without
from datetime import datetime
from math import sin, cos, atan
import utm
from util import distance, swap_coords

from pprint import pprint


def swap_coords(coords):
    return [coords[1], coords[0]]


class Bike(Document):
    point = PointField()
    speed = FloatField(default=0)
    heading = FloatField(default=0)
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

    def get_xy(self):
        return utm.from_latlon(*swap_coords(self.point))

    def set_xy(self, x, y, ZONE_NUMBER, ZONE_LETTER):
        self.point = swap_coords(utm.to_latlon(x, y, ZONE_NUMBER, ZONE_LETTER))

    def update(self, new_point):
        (x1, y1,
         ZONE_NUMBER,
         ZONE_LETTER) = self.get_xy()

        (x2, y2,
         ZONE_NUMBER,
         ZONE_LETTER) = utm.from_latlon(*swap_coords(new_point))

        tdelta = datetime.now() - self.stamp
        seconds = tdelta.total_seconds()

        self.speed = distance(x1, y1, x2, y2) / seconds

        try:
            self.heading = atan((y2-y1) / (x2-x1))
        except ZeroDivisionError:
            self.heading = 0

        self.stamp = datetime.now()
        self.point = new_point

    def delta_x(self):
        tdelta = datetime.now() - self.stamp
        seconds = tdelta.total_seconds()

        distance = seconds * self.speed

        return sin(self.heading) * distance

    def delta_y(self):
        tdelta = datetime.now() - self.stamp
        seconds = tdelta.total_seconds()

        distance = seconds * self.speed
        return cos(self.heading) * distance
