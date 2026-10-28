import geopandas as gpd
import random
import shapely as shp
import networkx as nx
import pandas as pd
from plot import plot
from fill import fill
import scipy
import numpy as np

london_postcodes = pd.read_csv('london_postcodes.csv')['postcode_area']
postcode_areas = gpd.GeoDataFrame(columns=['postcode', 'geometry'])
for _, postcode in london_postcodes.items():
    print(postcode)
    postcodes = gpd.read_file(f'codepp_essh_gb/Polygons/Data/POLYGONS/SHAPE_AB_ZE/{postcode}.shp')
    postcodes['outer'] = postcodes['POSTCODE'].str.replace(" ", "").str[:-3]
    postcodes['outer'] = postcodes['outer'].apply(lambda x: x[:-1] if x[-1].isalpha() else x)
    postcodes_clean = postcodes[~postcodes['outer'].str.startswith('V')]
    postcodes_gdf = postcodes_clean.dissolve(by='outer').explode()
    postcodes_gdf['geometry'] = postcodes_gdf['geometry'].apply(lambda x: shp.Polygon(x.exterior.coords))
    postcodes_gdf = postcodes_gdf.reset_index()

    postcode_areas = pd.concat([postcode_areas, postcodes_gdf[['outer', 'geometry']]])

postcode_areas = postcode_areas.to_crs(4326)
postcode_areas = postcode_areas.overlay(greater_london_river, how='intersection')

colours = random.choices(
    ['#CC0000',  # red
     '#E69138',  # orange
     '#F1C232',  # yellow
     #'#0986BE',  # indigo
     '#893C80'],  # violet
    k=len(postcode_areas))
postcode_areas['colour'] = colours
postcode_areas['area'] = postcode_areas['geometry'].area * 1000
postcode_areas.sort_values(by='area', inplace=True)
postcode_areas_largest = postcode_areas.drop_duplicates(subset='outer', keep='last')
postcode_areas_dupes = postcode_areas[~postcode_areas.index.isin(postcode_areas_largest.index)]
plot((postcode_areas_largest, {'color': postcode_areas['colour']}))
plot((postcode_areas[postcode_areas['outer'] == 'EC3'], {'color': postcode_areas['colour']}))



# postcodes
postcodes['outer'] = postcodes['postcode'].str.replace(" ", "").str[:-3]


sw = postcodes[postcodes['outer'] == 'SW2']
sw_list = list(sw['geometry'])
sw_arr = np.array([[p.x, p.y] for p in sw_list])
sw_vor = vor = scipy.spatial.Voronoi(sw_arr)
lines = [shp.geometry.LineString(vor.vertices[line]) for line in vor.ridge_vertices if -1 not in line]
poly = shp.polygonize(lines)
poly = list(poly.geoms)
poly = gpd.GeoDataFrame(geometry=poly, crs=27700)

postcodes_clean = postcodes[~postcodes['outer'].str.startswith('V')]
vertical_streets = postcodes[postcodes['outer'].str.startswith('V')]
postcodes_gdf = postcodes_clean.dissolve(by='outer').explode()
postcodes_gdf['geometry'] = postcodes_gdf['geometry'].apply(lambda x: shp.Polygon(x.exterior.coords))



postcode_graph = polygons_to_graph(postcode_areas_largest)


def postcode_graph(postcodes):
    start_nodes = []
    end_nodes = []
    attributes = []

    for j in range(len(postcodes)):
        postcode = postcodes.iloc[j]['geometry']
        intersects = roads.intersects(road)
        # only proceed if the road intersects with itself and at least two others (endpoints)
        if sum(intersects) >= 3:
            intersections = roads[intersects].intersection(road)
            intersections = gpd.GeoDataFrame(geometry=intersections[intersections.geom_type == 'Point'])
            multiPoint = intersections.dissolve().iloc[0]['geometry']
            edges = shp.ops.split(road, multiPoint)
            for i in range(len(edges.geoms)):
                start_nodes.append(edges.geoms[i].boundary.geoms[0])
                end_nodes.append(edges.geoms[i].boundary.geoms[1])
                attributes.append(edges.geoms[i])
            if j % 100 == 0: print(j)

    attributes = [{'connection': x} for x in attributes]
    edge_list = list(zip(start_nodes, end_nodes, attributes))
    graph = nx.MultiGraph()
    graph.add_edges_from(edge_list)

    return graph

