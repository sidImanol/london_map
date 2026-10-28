from shapely.geometry import box
import geopandas as gpd
from preprep_data import chunk_intersection, get_data
import matplotlib.pyplot as plt

crs = 25830 # Spain

data_types = {
    'roads': 'gis_osm_roads_free_1',
    'natural': 'gis_osm_natural_free_1',
    'landuse': 'gis_osm_landuse_a_free_1',
    'water': 'gis_osm_water_a_free_1',
}


# rectangle in lat/lon
rect_wgs = box(-2.01, 43.30, -1.96, 43.33)
gdf = gpd.GeoDataFrame({'geometry':[rect_wgs]}, crs="EPSG:4326")
boundary_gdf = gdf.to_crs(crs)

data = get_data(
    folder='pais-vasco-260305-free.shp',
    data_types=data_types,
    crs=crs)

for data_type in data:
    chunk_intersection(data[data_type], boundary_gdf, data_type, f'data/intermediary/donostia/')



roads = gpd.read_file('data/intermediary/donostia/roads/roads.shp')
water = gpd.read_file('data/intermediary/donostia/water/water.shp')
natural = gpd.read_file('data/intermediary/donostia/natural/natural.shp')
landuse = gpd.read_file('data/intermediary/donostia/landuse/landuse.shp')

roads_polygons = roads[
    roads.fclass.isin([
        'residential',
        'secondary',
        'tertiary',
        'primary',
        'pedestrian',
        'motorway'
    ])
]
roads_polygons['geometry'] = roads_polygons['geometry'].buffer(2)


f, ax = plt.subplots(figsize=(46, 33))
ax.set_facecolor('#CDF9FC')
landuse.plot(ax=ax, color='red')
water.plot(ax=ax, color='#CDF9FC')
roads_polygons.plot(ax=ax, column='fclass')
plt.show()
