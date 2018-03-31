import urllib2
from LatLon import LatLon, Latitude, Longitude
import json


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
    try:
        route = json.loads(geojson)
        return [(c[0], c[1])
                for c in route['features'][0]['geometry']['coordinates']]
    except ValueError:
        return []


class Router:
    """
    intended use:
        router = Router(points=[LatLon(Longitude(-99.1655), Latitude(19.342)),
                                LatLon(Longitude(-99.1611), Latitude(19.340))])
        coarse_route = router.route
        fine_route = router.get_refined_route(speed=10)  # speed in m/s
        finer_route = router.get_refined_route(speed=3)  # speed in m/s
    """

    def __init__(self, points,
                 protocol='http', host='localhost', port=17777):
        self.points = points
        self.server = "{protocol}://{host}:{port}".format(
            protocol=protocol,
            host=host,
            port=port)
        self.update_route()

    def update_route(self):
        """
        Use brouter server to get route
        """
        P = []
        for p in self.points:
            P.append("%s,%s" % (p.lon, p.lat))
        lonlats = "|".join(P)

        route_url = "{server}" \
                    + "/brouter?lonlats={lonlats}" \
                    + "&profile=trekking&alternativeidx=0&format=geojson"

        route_url = route_url.format(
            server=self.server,
            lonlats=lonlats)
#        try:
        response = urllib2.urlopen(route_url)
        broute_json = response.read()
        self.route = route_from_geojson(broute_json)
#        except:
           # pass

    def get_refined_route(self, speed):
        return refine(self.route, speed)
