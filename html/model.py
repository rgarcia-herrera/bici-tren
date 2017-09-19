from mongoengine import Document, FloatField, \
    DateTimeField, PointField, LineStringField, \
    connect  # must import connect, used from without
from datetime import datetime
from math import atan, degrees
import utm
from util import distance, swap_coords
import svgwrite


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
        new_point = swap_coords(utm.to_latlon(x, y, ZONE_NUMBER, ZONE_LETTER))
        self.update(new_point)

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
        except:
            self.heading = 0

        self.stamp = datetime.now()
        self.point = new_point


    def flecha(self, color='green'):
        dwg=svgwrite.Drawing()
        dwg.viewbox(width=100, height=100)
        p = svgwrite.shapes.Polygon(points=[[50,20], [30, 80], [70,80]], fill=color, opacity=0.3)
        p.rotate(degrees(self.heading),
                 center=(50,50))
        dwg.add(p)
        return dwg.tostring()
