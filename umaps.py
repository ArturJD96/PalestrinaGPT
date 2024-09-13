import umap

print('Fitting UMAP...')

mapper15 = umap.UMAP(random_state=1594, target_metric='l2', n_neighbors=15).fit_transform(segments_df)
umap_df15 = pd.DataFrame(mapper15, index=mi)

mapper45 = umap.UMAP(random_state=1594, target_metric='l2', n_neighbors=45).fit_transform(segments_df)
umap_df45 = pd.DataFrame(mapper45, index=mi)

mapper120 = umap.UMAP(random_state=1594, target_metric='l2', n_neighbors=120).fit_transform(segments_df)
umap_df120 = pd.DataFrame(mapper120, index=mi)

mapper300 = umap.UMAP(random_state=1594, target_metric='l2', n_neighbors=300).fit_transform(segments_df)
umap_df300 = pd.DataFrame(mapper300, index=mi)

from pathlib import Path

DATA_DIR = Path('data')

dataframes = {
    # 'segments': segments_df,
    # 'segments_notation': segments_notation_df,
    'umap_l2_neighbours15': umap_df15,
    'umap_l2_neighbours45': umap_df45,
    'umap_l2_neighbours120': umap_df120,
    'umap_l2_neighbours300': umap_df300
}

for name, df in dataframes.items():
    df.to_pickle(DATA_DIR/f'{name}.pkl')
