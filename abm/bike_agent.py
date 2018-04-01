import agent
from pony.orm import select


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

    def __init__(self, bikes):
        lats = list()
        lons = list()
        speeds = []
        for b in bikes:
            speeds.append(b.speed)
            lats.append(b.point['coordinates'][0])
            lons.append(b.point['coordinates'][1])

        self.mean_speed = sum(speeds) / float(len(speeds))
        self.centroid = (sum(lats) / float(len(lats)),
                         sum(lons) / float(len(lons)))


class Bike(agent.Agent):

    def get_flock_candidates(self, my_radius, dest_radius):
        p_w_lon, p_e_lon, p_s_lat, p_n_lat = bounding_box(self.point())
        d_w_lon, d_e_lon, d_s_lat, d_n_lat = bounding_box(self.destination())

        precandidates = select(b for b in Bike
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
