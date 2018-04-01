from pony import orm
from router import Router
from datetime import datetime
from LatLon import LatLon, Latitude, Longitude
from pony.orm import select

db = orm.Database()


def bounding_box(point, degrees=0.1):
    w_lon = float(point.lon) - degrees
    e_lon = float(point.lon) + degrees
    s_lat = float(point.lat) - degrees
    n_lat = float(point.lat) + degrees
    return w_lon, e_lon, s_lat, n_lat


class Flock:
    """
    Flock object is created from a list of agents
    and has a useful centroid
    """
    def __init__(self, agents):
        lats = list()
        lons = list()
        speeds = []
        for b in agents:
            speeds.append(b.speed)
            lats.append(float(b.point().lat))
            lons.append(float(b.point().lon))

        self.mean_speed = sum(speeds) / float(len(speeds))
        self.centroid = LatLon(Latitude(sum(lats) / len(lats)),
                               Longitude(sum(lons) / len(lons)))


class Agent(db.Entity):
    lon = orm.Required(float, default=0)
    lat = orm.Required(float, default=0)
    speed = orm.Required(float, default=0)
    heading = orm.Required(float, default=0)
    destination_heading = orm.Required(float, default=0)
    dest_lon = orm.Required(float, default=0)
    dest_lat = orm.Required(float, default=0)
    stamp = orm.Required(datetime, default=datetime.now)
    route = orm.Required(orm.Json, default={})
    # route_flock = LineStringField()
    status = orm.Required(str, default="solo")

    point_altruism = orm.Required(float, default=0.1)
    dest_altruism = orm.Required(float, default=0.2)

    def point(self):
        return LatLon(Latitude(self.lat),
                      Longitude(self.lon))

    def set_point(self, point):
        self.lat = float(point.lat)
        self.lon = float(point.lon)

    def destination(self):
        return LatLon(Latitude(self.dest_lat),
                      Longitude(self.dest_lon))

    def set_destination(self, point):
        self.dest_lat = float(point.lat)
        self.dest_lon = float(point.lon)

    def to_dict(self):
        return {'agent_id': "%s" % self.id,
                'point': {'coordinates': [self.lon,
                                          self.lat]},
                'status': self.status,
                'in': True if self.status == 'flocking' else False,
                'speed': self.speed,
                'heading': float("%0.2f" %
                                 self.heading),
                'destination_heading': float("%0.2f" %
                                             self.destination_heading),
                'destination': {'coordinates': [self.dest_lon,
                                                self.dest_lat]},
                'stamp': str(self.stamp)}

    def __str__(self):
        return "<A-%s [%s] %0.2fm @%sm/s>" % (str(self.id)[-3:],
                                              self.status,
                                              self.distance_to(
                                                  self.destination()),
                                              self.speed)

    def update(self, new_point, update_speed=False):
        """
        updates time stamp

        uses @new_point to update:
         - point
         - heading
         - destination_heading
         - speed, if update_speed=True

        """
        self.heading = self.point().heading_initial(new_point)

        self.destination_heading = new_point.heading_initial(
            self.destination())

        if update_speed:
            tdelta = datetime.now() - self.stamp
            seconds = tdelta.total_seconds()
            distance = self.point().distance(new_point) / 1000.0
            self.speed = distance / seconds

        self.stamp = datetime.now()
        self.set_point(new_point)

    def heading_to(self, other_point):
        """
        heading from my point to @other_point
        """
        return self.point().heading_initial(other_point)

    def distance_to(self, other_point):
        """
        distance from agent to another point, in metres
        @other_point must be type LatLon
        """
        return self.point().distance(other_point) * 1000.0

    def got_there(self):
        """
        return True if one step or less away
        """
        if self.distance_to(self.destination()) < self.speed:
            return True
        else:
            return False

    def update_route(self, points=[]):
        """
        Include intermediate points between my point and my destination.
        If no intermediate points given, just download route from my
        point to my destination.
        """
        router = Router(points=[self.point(), ]
                        + points
                        + [self.destination(), ])
        if router.route:
            self.route = router.get_refined_route(self.speed)
            return True
        else:
            return False

    def step(self):
        """
        move to next point in route
        """
        if self.route:
            p = self.route.pop(0)
            p = LatLon(Latitude(p[1]),
                       Longitude(p[0]))
        else:
            p = self.destination()

        self.update(p)

    def flocking(self):
        p_w_lon, p_e_lon, p_s_lat, p_n_lat = bounding_box(self.point(),
                                                          degrees=0.0001)
        return select(b for b in Agent
                      if b.id != self.id
                      and b.lon > p_w_lon
                      and b.lon < p_e_lon
                      and b.lat > p_s_lat
                      and b.lat < p_n_lat).count() > 0

    def get_flock_candidates(self, my_radius, dest_radius):
        p_w_lon, p_e_lon, p_s_lat, p_n_lat = bounding_box(self.point())
        d_w_lon, d_e_lon, d_s_lat, d_n_lat = bounding_box(self.destination())

        precandidates = select(b for b in Agent
                               if b.id != self.id
                               and b.lon > p_w_lon
                               and b.lon < p_e_lon
                               and b.lat > p_s_lat
                               and b.lat < p_n_lat

                               and b.dest_lon > d_w_lon
                               and b.dest_lon < d_e_lon
                               and b.dest_lat > d_s_lat
                               and b.dest_lat < d_n_lat)

        candidates = []
        for c in precandidates:
            if self.point().distance(c.point()) < my_radius \
               and self.destination().distance(c.destination()) < dest_radius:
                candidates.append(c)

        return candidates

    def flock(self):
        if self.flocking():
            self.status = "flock"
        else:
            ride_length = self.point().distance(self.destination())
            my_radius = ride_length * self.point_altruism
            dest_radius = ride_length * self.dest_altruism
            candidates = self.get_flock_candidates(my_radius, dest_radius)
            if candidates:
                f = Flock(candidates)
                if self.update_route(points=[f.centroid, ]):
                    self.status = "flocking"
            else:
                self.status = "solo"
