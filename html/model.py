from mongoengine import Document, FloatField, \
    DateTimeField, PointField, LineStringField, \
    connect  # must import connect, used from without
from datetime import datetime
from math import sqrt, sin, cos
import utm

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
                'predicted_point': self.predicted_point(),
                'speed': self.speed,
                'heading': self.heading,
                'destination': self.destination,
                'stamp': str(self.stamp)}

    def __str__(self):
        return "<bike %s %s @%sm/s>" % (self.id, self.point, self.speed)

    def update(self, new_point):
        (x1, y1,
         ZONE_NUMBER,
         ZONE_LETTER) = utm.from_latlon(*swap_coords(self.point))

        self.point = new_point

        (x2, y2,
         ZONE_NUMBER,
         ZONE_LETTER) = utm.from_latlon(*swap_coords(new_point))

        now = datetime.now()
        tdelta = now - self.stamp
        seconds = tdelta.total_seconds()

        self.speed = sqrt((x2 - x1)**2 * (y2 - y1)**2) / seconds

        try:
            self.heading = (x2 - x1) / (y2 - y1)
        except ZeroDivisionError:
            self.heading = 0

        self.stamp = now

    def predicted_point(self):
        (x1, y1,
         ZONE_NUMBER,
         ZONE_LETTER) = utm.from_latlon(
             *swap_coords(self.point['coordinates']))

        x2 = x1 + cos(self.heading) * self.speed
        y2 = y1 + sin(self.heading) * self.speed

        return swap_coords(utm.to_latlon(x2, y2,
                                         ZONE_NUMBER,
                                         ZONE_LETTER))

    # def update_current_segment(self):
    #     a = [[self.point[0],
    #           self.point[1]],
    #          [self.predicted_point()[0],
    #           self.predicted_point()[1]]]
    #     pprint(a)
    #     self.current_segment = {'type': 'LineString',
    #                             'coordinates': a}

    # def route(self):
    #     route = json.loads(
    #         urllib2.urlopen(route_url % (self.point[0],
    #                                      self.point[1],
    #                                      self.destination[0],
    #                                      self.destination[1])).read())
    #     coords = route['features'][0]['geometry']['coordinates']
    #     pprint(coords)
    #     return coords
