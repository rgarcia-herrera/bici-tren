from mongoengine import Document, connect, GeoPointField, FloatField, \
    DateTimeField
from datetime import datetime
from math import sqrt
import utm


class Bike(Document):
    point = GeoPointField()
    speed = FloatField(default=0)

    stamp = DateTimeField(default=datetime.now)

    def __str__(self):
        return "<bike %s %s @%sm/s>" % (self.id, self.point, self.speed)

    def update(self, point):

        (x1, y1,
         ZONE_NUMBER, ZONE_LETTER) = utm.from_latlon(*self.point)

        self.point = point

        (x2, y2,
         ZONE_NUMBER, ZONE_LETTER) = utm.from_latlon(*self.point)

        now = datetime.now()
        tdelta = now - self.stamp
        seconds = tdelta.total_seconds()
        
        self.speed = sqrt((x2 - x1)**2 * (y2 - y1)**2) / seconds
        self.stamp = now

        self.save()
