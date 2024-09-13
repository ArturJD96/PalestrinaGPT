import pandas as pd
import music21 as m21
import numpy as np

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

segments = [[[*decode_note(note), i] for i, note in enumerate(segment)] for segment in df.values.tolist()]
segments = np.array(segments)

fig = go.Figure()
for i, segment in enumerate(segments[:5000]):
    # remove all non-existent points (but appearing due to index present)
    segment = np.array([note for note in segment if note[0]]) # get rid of conversion
    pitch = segment[:,0]
    duration = segment[:,1]
    index = segment[:,2]
    fig.add_trace(go.Scatter3d(
        x=duration,
        y=index,
        z=pitch,
        mode='lines',
        name=df.index[i][1]))

# fig.update_zaxes(type="log")
fig.update_layout(
    title="Shapes of Palestrina segments (duration explicit)",
    scene=dict(xaxis_title="Duration (quaver)",
               yaxis_title="Number of note in the melody",
               zaxis_title="Pitch (midi)",
               xaxis_type='log'),
    legend_title="Segment source")

if __name__ == '__main__':
    fig.show()
