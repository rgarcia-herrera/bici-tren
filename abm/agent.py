from mongoengine import Document, FloatField, \
    DateTimeField, PointField, LineStringField
from datetime import datetime
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
    meta = {'allow_inheritance': True}

    def to_dict(self):
        return {'agent_id': "%s" % self.id,
                'point': self.point,
                'speed': self.speed,
                'heading': float("%0.2f" %
                                 self.heading),
                'destination_heading': float("%0.2f" %
                                             self.destination_heading),
                'destination': self.destination,
                'stamp': str(self.stamp)}

    def __str__(self):
        return "<A-%s %0.2fm @%sm/s>" % (str(self.id)[-3:],
                                         self.distance_to(
                                             self.destination),
                                         self.speed)

    def get_point_LatLon(self):
        return LatLon(Longitude(self.point['coordinates'][1]),
                      Latitude(self.point['coordinates'][0]))

    def update(self, new_point, update_speed=False):
        """
        updates time stamp

        uses @new_point to update:
         - point
         - heading
         - destination_heading
         - speed, if update_speed=True

        """

        if 'coordinates' in self.point:
            a = LatLon(Longitude(self.point['coordinates'][1]),
                       Latitude(self.point['coordinates'][0]))
        else:
            a = LatLon(Longitude(self.point[1]),
                       Latitude(self.point[0]))

        if 'coordinates' in new_point:
            b = LatLon(Longitude(new_point['coordinates'][1]),
                       Latitude(new_point['coordinates'][0]))
        else:
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

        if update_speed:
            tdelta = datetime.now() - self.stamp
            seconds = tdelta.total_seconds()
            distance = a.distance(b) / 1000.0
            self.speed = distance / seconds

        self.stamp = datetime.now()
        self.point = new_point
        self.save()

    def heading_to(self, other_point):
        """
        heading from my point to @other_point
        """
        a = LatLon(Longitude(self.point['coordinates'][1]),
                   Latitude(self.point['coordinates'][0]))

        b = LatLon(Longitude(other_point[1]),
                   Latitude(other_point[0]))

        return a.heading_initial(b)

    def distance_to(self, other_point):
        """
        distance from agent to another point, in metres
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

    def get_near_agents(self, radius):
        return Agent.objects(point__near=self.point,
                             point__max_distance=radius)  # incluir heading?

    def got_there(self):
        """
        return True if one step or less away
        """
        if self.distance_to(self.destination) < self.speed:
            return True
        else:
            return False

    def step(self):
        """
        move to next point in route
        """
        self.reload()
        if self.route is None:
            self.update(self.destination)
        else:
            coordinates = self.route['coordinates'][:]
            if len(coordinates) == 2:
                p = coordinates[0]
                self.route = None
            else:
                p = coordinates.pop(0)
                self.route = coordinates

            self.save()
            self.update(p)
