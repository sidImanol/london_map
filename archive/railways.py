import pandas as pd
import geopandas as gpd
from datetime import datetime


def join_lines(df):
    boundaries = df[['osm_id', 'geometry']]
    boundaries_0 = boundaries.copy()
    boundaries_0['geometry'] = boundaries_0['geometry'].apply(lambda x: x.boundary.geoms[0])
    boundaries_0['direction'] = 0

    boundaries_1 = boundaries.copy()
    boundaries_1['geometry'] = boundaries_1['geometry'].apply(lambda x: x.boundary.geoms[1])
    boundaries_1['direction'] = 1

    boundaries = pd.concat([boundaries_0, boundaries_1])
    boundaries.set_index(['osm_id', 'direction'], inplace=True)
    boundaries = boundaries['geometry']
    ids = list(df['osm_id'])
    id_dict = {id: 0 for id in ids}
    group = 0
    while len(boundaries) > 0:
        seed_id = boundaries.index[0][0]
        seed_indices = boundaries.index[boundaries.index.get_level_values('osm_id') == seed_id]
        group += 1
        id_dict[seed_id] = group
        for seed_index in seed_indices:
            boundary = boundaries[seed_index]
            boundaries.drop(seed_index, inplace=True)

            matches = 1
            while matches == 1:
                indices = boundaries[boundaries == boundary].index
                boundaries.drop(indices, inplace=True)
                matches = len(indices)
                if matches == 1:
                    neighbour_id = indices[0][0]
                    direction = 1 - indices[0][1]
                    id_dict[neighbour_id] = group

                    multi_index = (neighbour_id, direction)
                    if multi_index in boundaries.index:
                        boundary = boundaries[multi_index]
                        boundaries.drop(multi_index, inplace=True)
                    else:
                        matches = 0

    for osm_id in id_dict:
        if id_dict[osm_id] == 0:
            group += 1
            id_dict[osm_id] = group


railways = gpd.read_file('intermediary_data/railways.shp')

subway = railways[railways['fclass'] == 'subway']
train = railways[railways['fclass'] == 'rail']
dlr = railways[(railways['fclass'] == 'light_rail') & railways['name'].isin(['Docklands Light Railway', 'DLR', 'Canning Town Flyover'])]
tram = railways[railways['fclass'] == 'tram']
rail = pd.concat([train, dlr, tram, subway])


id_groups_df = pd.DataFrame.from_dict(id_dict, orient='index').rename(columns={0: 'group'})
groups = pd.read_csv('data/groups.csv')
joined_railways = join_lines(rail)
joined_railways.reset_index(inplace=True)

# get depots and sidings
sidings = rail[rail['name'].str.lower().str.contains('siding', na=False)][['osm_id']]
depot = rail[rail['name'].str.lower().str.contains('depot', na=False)][['osm_id']]
joined_railways_exploded = joined_railways.explode('osm_ids').rename(columns={'osm_ids': 'osm_id'})
sidings_groups = sidings.merge(joined_railways_exploded, how='left', on='osm_id').rename(columns={'index': 'group'})
depot_groups = depot.merge(joined_railways_exploded, how='left', on='osm_id').rename(columns={'index': 'group'})


exception_groups = pd.read_csv('data/rail_groups.csv')
exclusion_ids = joined_railways[
    joined_railways['index'].isin(exception_groups['group'])
    | joined_railways['index'].isin(sidings_groups['group'])
    | joined_railways['index'].isin(depot_groups['group'])
]['osm_ids']
exclusion_id_list = []

for id_list in exclusion_ids:
    exclusion_id_list.extend(id_list)

exclusion_id_df = pd.DataFrame(exclusion_id_list, columns=['osm_id'])
exclusion_id_df.to_csv('intermediary_data/lines/excluded_ids', index=False)


exclusion_id_df = pd.read_csv('intermediary_data/lines/excluded_ids', dtype=str)

rail_clean = rail[~rail['osm_id'].isin(exclusion_id_df['osm_id'])]
plot((rail_clean, {'linestyle': 'dashed'}))
map = rail_clean.explore()
map.save('railways.html')

rail_clean.to_file('intermediary_data/rail_clean.shp')

rail_clean_groups = joined_railways[
    ~joined_railways['index'].isin(sidings_groups['group'])
    & ~joined_railways['index'].isin(depot_groups['group'])
    & ~joined_railways['index'].isin(exception_groups['group'])
]

plot((rail_clean, {'color': 'b'}))
