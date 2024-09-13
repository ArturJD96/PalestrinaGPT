import numpy as np
import pandas as pd
# import matplotlib.pyplot as plt
import plotly.graph_objects as go
import umap

# Based on:
# https://umap-learn.readthedocs.io/en/latest/embedding_space.html

data = pd.read_pickle('data_vis/segments.pkl')

# print(data.index['scala'])

def sphere2cart(sphere_mapper):
    # Get axes
    x = np.sin(sphere_mapper.embedding_[:, 0]) * np.cos(sphere_mapper.embedding_[:, 1])
    y = np.sin(sphere_mapper.embedding_[:, 0]) * np.sin(sphere_mapper.embedding_[:, 1])
    z = np.cos(sphere_mapper.embedding_[:, 0])
    # Convert to 2d
    x = np.arctan2(x, y)
    y = -np.arccos(z)
    return x, y

sphere_mapper = umap.UMAP(output_metric='haversine', random_state=42).fit(data)
x, y = sphere2cart(sphere_mapper)

fig = go.Figure(go.Scatter(x=x, y=y, mode='markers'))
fig.show()
