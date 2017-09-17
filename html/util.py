from math import sqrt, atan, sin, cos


def swap_coords(coords):
    return [coords[1], coords[0]]


def distance(x1, y1, x2, y2):
    """ returns distance between two northing-easting points """
    return sqrt((x1-x2)**2 + (y1-y2)**2)


def segment(a, b, dist):
    wp = []
    for i in range(1, int(distance(a[0], a[1], b[0], b[1])/dist)):
        try:
            heading = atan((b[1]-a[1]) / (b[0]-a[0]))
        except:
            heading = 0

        dx = cos(heading) * (dist * i)
        dy = sin(heading) * (dist * i)

        wp.append([a[0] + dx, a[1] + dy])
    return wp
