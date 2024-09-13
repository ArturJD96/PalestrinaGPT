import numpy as np
import pandas as pd
# import matplotlib.pyplot as plt
import plotly.graph_objects as go
import umap

data = pd.read_pickle('data_vis/segments.pkl')

sphere_mapper = umap.UMAP(metric='hellinger', random_state=42).fit_transform(data)

fig = go.Figure(go.Scatter(x=sphere_mapper[:,0], y=sphere_mapper[:,1], mode='markers'))
fig.show()
