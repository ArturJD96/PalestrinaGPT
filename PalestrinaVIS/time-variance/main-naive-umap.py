import pandas as pd
import music21 as m21
import numpy as np
import umap
import umap.plot

from plotly.subplots import make_subplots
import plotly.graph_objects as go
import plotly.express as px

def decode_note(note:str, return_none=True) -> list[int|None]:
    if not note: return [None, None] if return_none else [-1, -1]
    pitch, duration = note.split('|')
    dur_type, dot = None, None
    if '(' in duration:
        dur_type, dot = duration.split('(')
        dot = 1
    else:
        dur_type = duration
        dot = 0
    pitch = m21.pitch.Pitch(pitch).midi
    dur = int(m21.duration.Duration(dur_type, dots=dot).quarterLength * 2)
    # dot = divmod(duration, 4)[1] == 0
    return [pitch, dur]

df = pd.read_pickle('data_vis/segments_notation.pkl')

# [[67  8  1  0]
#  [74  4  1  0]
#  [79  4  1  0]
#  ...
#  [60  4  1  0]
#  [55  8  1  0]
#  [55  4  1  0]]

segment_limit = 1000;
note_limit = 127

all_segments = [[decode_note(note, return_none=False) for i, note in enumerate(segment)] for segment in df.values.tolist()]
all_segments = np.array(all_segments)
all_segments_lengths = np.argmax(all_segments < 0, axis=1, keepdims=True)

print(all_segments.shape) # (45650, 127, 2)

segments = all_segments[:segment_limit,:note_limit]
segments = np.array([segments[:,d] for d in range(segments.shape[1])])

relations:dict = {i:i for i in range(segments.shape[1])}
rel_dicts:list[dict] = [relations.copy() for i in range(segments.shape[0] - 1)]

'''
TO DO: remove note repetitions going to the umap
       by correctly relating points.
'''

aligned_mapper = umap.AlignedUMAP().fit(segments.tolist(), relations=rel_dicts)
embeddings = np.array(aligned_mapper.embeddings_)

print(embeddings.shape) # (127, 10, 2)

fig = go.Figure()

# '''Show by level'''
# for note_index, embeddings in enumerate(aligned_mapper.embeddings_):
#     fig.add_trace(go.Scatter3d(
#         x=embeddings[:,0],
#         y=embeddings[:,1],
#         z=np.full(embeddings.shape[0], note_index),
#         customdata=df[note_index].values,
#         hovertemplate="<b>%{customdata}</b>",
#         mode='lines'))

'''Show by segment'''
embeddings_per_segment = [embeddings[:,segment_id] for segment_id in range(segment_limit)]
for segment_id, segment_embeddings in enumerate(embeddings_per_segment):
    levels = segment_embeddings.shape[0]
    x_limit = all_segments_lengths[segment_id,0,0]
    y_limit = all_segments_lengths[segment_id,0,1]
    durations = (all_segments[segment_id,:y_limit,1]/2).cumsum()
    # print(x_limit)
    # print(y_limit)
    # print(durations)
    x = segment_embeddings[:x_limit,0]
    y = segment_embeddings[:y_limit,1]
    fig.add_trace(go.Scatter3d(
        x=x,
        y=y,
        # z=np.linspace(0, levels-1, num=levels), # (duration/2).cumsum(),
        z=durations,
        customdata=df.iloc[segment_id],
        hovertemplate="<b>%{customdata}</b>",
        mode='lines'))

fig.show()

# current_target = ordered_target[150 * i:min(ordered_target.shape[0], 150 * i + 400)]
# ax.scatter(*aligned_mapper.embeddings_[i].T, s=2, c=current_target, cmap="Spectral")



# mapper = umap.UMAP(random_state=1594, tqdm_kwds=dict(desc='Mapping')).fit(segments[:,note_index])
# embeddings = mapper.transform(segments[:,note_index])

# fig = go.Figure()
# fig.add_trace(go.Scatter(
#     x=embeddings[:,0],
#     y=embeddings[:,1],
#     customdata=df[note_index].values,
#     hovertemplate="<b>%{customdata}</b>",
#     mode='markers'))
# fig.show()




# fig.update_zaxes(type="log")
# fig.update_layout(
#     title="Shapes of Palestrina segments (duration explicit)",
#     scene=dict(xaxis_title="Duration (quaver)",
#                yaxis_title="Number of note in the melody",
#                zaxis_title="Pitch (midi)",
#                xaxis_type='log'),
#     legend_title="Segment source")

# if __name__ == '__main__':
#     fig.show()
