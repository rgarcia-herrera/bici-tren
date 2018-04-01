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
