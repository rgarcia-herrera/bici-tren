from mongoengine import Document, FloatField, \
    DateTimeField, PointField, LineStringField, \
    connect  # must import connect, used from without
from datetime import datetime
import svgwrite
from LatLon import LatLon, Latitude, Longitude


class Agent(Document):
    point = PointField()
    speed = FloatField(default=0)
    heading = FloatField(default=0)
    destination_heading = FloatField(default=0)
    destination = PointField(required=False)
    stamp = DateTimeField(default=datetime.now)
    route = LineStringField()
    # route_flock = LineStringField()
    # status = StringField()

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
        return "<bike %s %s away @%sm/s>" % (self.id,
                                             self.distance_to(
                                                 self.destination),
                                             self.speed)

    def get_point_LatLon(self):
        return LatLon(Longitude(self.point['coordinates'][1]),
                      Latitude(self.point['coordinates'][0]))

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

    def step(self):
        self.reload()
        p, got_there = self.towards(self.route['coordinates'][0])
        if not got_there:
            print "hacia el primer punto"
            self.update(p)
        else:
            print "actualizar ruta"
            self.update_route(self.destination)
