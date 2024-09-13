import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
import umap
import plotly.graph_objects as go

df = pd.read_pickle('data_vis/segments_notation.pkl')
phrases = [' '.join([str(note) for note in phrase if note is not None]) for phrase in df.values.tolist()]
df_phrases = pd.DataFrame(phrases, index=df.index)

# vectorizer = CountVectorizer(min_df=5, stop_words='english')
# word_doc_matrix = vectorizer.fit_transform(dataset.data)
# embedding = umap.UMAP(n_components=2, metric='hellinger').fit(word_doc_matrix)
# f = umap.plot.points(embedding, labels=hover_df['category'])

text = [phrase[0] for phrase in df_phrases.values.tolist()]

tfidf_vectorizer = TfidfVectorizer(lowercase=False)#(min_df=1, stop_words='english')
tfidf_word_doc_matrix = tfidf_vectorizer.fit_transform(text)

# 3d
# tfidf_embedding = umap.UMAP(metric='hellinger', n_components=3).fit_transform(tfidf_word_doc_matrix)
# fig = go.Figure(go.Scatter3d(
#     x=tfidf_embedding[:,0],
#     y=tfidf_embedding[:,1],
#     z=tfidf_embedding[:,2], mode='markers'))
# fig.show()

# 2d
tfidf_embedding = umap.UMAP(metric='hellinger', n_components=2).fit_transform(tfidf_word_doc_matrix)
fig = go.Figure(go.Scatter(
    x=tfidf_embedding[:,0],
    y=tfidf_embedding[:,1],
    mode='markers'))
fig.show()
