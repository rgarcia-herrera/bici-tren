import json
import urllib2
import osmnx as ox, networkx as nx
from pprint import pprint

route_url = "http://h2096617.stratoserver.net:443/brouter?lonlats=-99.150946,19.365223|-99.156203,19.373746&nogos=&profile=trekking&alternativeidx=0&format=geojson"

route = json.loads(urllib2.urlopen(route_url).read())

ox.config(log_console=True, use_cache=True)

x = set()
y = set()
route_coords = route['features'][0]['geometry']['coordinates']
for wp in route_coords:
    x.add(wp[0])
    y.add(wp[1])

G = ox.graph_from_bbox(north=max(y),
                       south=min(y),
                       east=max(x),
                       west=min(x),
                       simplify=False,
                       clean_periphery=False,
                       network_type='bike')

# for wp in route_coords:
#     h = ox.graph_from_point((wp[1], wp[0]),
#                             100)
#     G.add_nodes_from(h.node)

osmid = {(G.node[n]['x'],
          G.node[n]['y']) : G.node[n]['osmid'] for n in G.nodes()}

plotroute = list()
for wp in route['features'][0]['geometry']['coordinates']:
    try:
        plotroute.append(osmid[(wp[0], wp[1])])
    except:
        pass

pprint( plotroute)
ox.plot_graph(G,
              use_geom=True,
              bgcolor='black',
              edge_linewidth=3,
              node_color='red',
              node_size=52)

