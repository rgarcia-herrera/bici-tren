from LatLon import LatLon, Latitude, Longitude
import requests


def split(s, t, speed):
    """
    returns points between s(ource) and t(arget) at intervals of size @speed
    """
    s = LatLon(Latitude(s[1]),
               Longitude(s[0]))

    t = LatLon(Latitude(t[1]),
               Longitude(t[0]))

    heading = s.heading_initial(t)

    fine = [(s.lon.decimal_degree,
             s.lat.decimal_degree), ]
    wp = s

    while True:
        dst = wp.offset(heading,
                        speed / 1000.0)

        if dst.distance(t) * 1000.0 > speed:
            fine.append((dst.lon.decimal_degree,
                         dst.lat.decimal_degree))
            wp = dst
        else:
            fine.append((t.lon.decimal_degree,
                         t.lat.decimal_degree))
            break

    return fine


def refine(route, speed):
    """
    returns a finer-grain route, splitting it at @speed intervals
    """
    assert len(route) > 1
    fine = [route[0], ]
    for i in range(len(route)-1):
        fine += split(route[i], route[i + 1], speed)[1:-1]
    fine.append(route[-1])
    return fine


def route_from_geojson(geojson):
    """
    returns just the coordinates list
    """
    return [(c[0], c[1])
            for c in geojson['features'][0]['geometry']['coordinates']]


class Router:
    """
    intended use:
        router = Router(protocol='http', host='localhost', port=17777)
        points = [LatLon(Latitude(19.461332069967366),
                         Longitude(-99.09204483032227)),
                  LatLon(Latitude(19.40467336236742),
                         Longitude(-99.17787551879884))]
        coarse_route = router.get_route(points=points)
        fine_route = router.get_route(points=points, speed=10)  # speed in m/s
        finer_route = router.get_route(points=points, speed=3)  # speed in m/s
    """

    def __init__(self,
                 protocol='http', host='localhost', port=17777):

        self.route_url = "{protocol}://{host}:{port}/brouter".format(
            protocol=protocol,
            host=host,
            port=port)

        self.session = requests.Session()

    def get_raw_route(self, points):
        """
        Use brouter server to get route thru points
        """
        lonlats = u"|".join(["%s,%s" % (p.lon, p.lat)
                             for p in points])

        params = "?lonlats=%s&profile=trekking&alternativeidx=0" % lonlats \
                 + "&format=geojson"

        response = self.session.get(self.route_url + params)

        try:
            return route_from_geojson(response.json())
        except ValueError:
            return []

    def get_route(self, points, speed=None):
        if speed:
            return refine(self.get_raw_route(points),
                          speed)
        else:
            return self.get_raw_route(points)
