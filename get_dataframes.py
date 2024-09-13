from pathlib import Path

from tqdm import tqdm
import pandas as pd

import music21 as m21
from music21.stream.base import Stream, Score

from PalestrinaUTILS.scores.Segment import Segment
from PalestrinaUTILS.scores.ScoreAnalyzer import ScoreAnalyzer

'''
This script:
    1) parses scores of Palestrina as music21 Streams;
    2) analyzes each score [using ScoreAnalyzer];
    3) segments each scores by voices (and then by rests) [using Segment];
    4) transforms segments into pandas dataframe records;
        1. 'segments_midi_padded' – pitch notation (midi) [PITCH ONLY THOUGH!]
        2. 'segments_notation' – descriptive notation of each note (e.g. 'G5|whole')
        NOTE: two versions of each: original & chiavetta resoloved.
    5) saves all dataframes to PalestrinaDATA/vis-dataframes/segments folder
'''

DATA_DIR = Path('PalestrinaDATA/vis-dataframes/segments')

'''Parse scores of Palestrina masses.'''
scores_iterator = tqdm(m21.corpus.getComposer('palestrina'), desc='Parsing scores')
scores:list[Stream] = [m21.corpus.parse(score_path) for score_path in scores_iterator]

'''Analyze each score – create a dict with resulting analysis.'''
analyzer = ScoreAnalyzer()
analyses:list[dict] = [analyzer(score) for score in tqdm(scores, desc='Analyzing scores')]

'''If score's chiavetta is high, transpose it to low chiavetta.'''
scores_chiavetta_resolved = [analyzer.resolve_chiavetta(score, analysis['chiavetta'], analysis['scala'], inPlace=False) for score, analysis in zip(scores, analyses)]

'''m21 scores + analyses -> pandas dataframes'''

databases = {
    'original_chiavetta': scores,
    'chiavetta_resolved': scores_chiavetta_resolved
}

for name, dataset in databases.items():

    '''Cut scores into segments.'''
    segments:list[Segment] = Segment.getSegmentsList(scores, analyses)
    segment_info:list[dict] = [segment.info for segment in segments]

    '''Change score info dict to pandas dict format (will serve as segment's index).'''
    segment_analyses = {k: [dic[k] for dic in segment_info] for k in segment_info[0]} # [0] is deliberate. See:https://stackoverflow.com/questions/5558418/list-of-dicts-to-from-dict-of-lists
    analyses_df = pd.DataFrame.from_dict(segment_analyses)
    mi = pd.MultiIndex.from_frame(analyses_df)

    segments_df = pd.DataFrame([segment.pitches for segment in segments], index=mi)
    segments_notation_df = pd.DataFrame([[f'{note.pitch.nameWithOctave}|{note.duration.type}'+('(dotted)' if note.duration.dots else '') for note in segment.notes] for segment in segments], index=mi)

    '''Save segments' databases.'''
    dataset_path = DATA_DIR/name
    dataset_path.mkdir(parents=True, exist_ok=True)
    segments_df.to_pickle(dataset_path/f'segments_midi_padded.pkl')
    segments_df.to_pickle(dataset_path/f'segments_notation.pkl')
