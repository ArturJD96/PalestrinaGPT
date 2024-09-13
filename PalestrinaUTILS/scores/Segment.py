from tqdm import tqdm
import music21 as m21
from music21.note import Note
from music21.stream.base import Stream

from PalestrinaUTILS.scores.ScoreAnalyzer import ScoreAnalysis

class Segment:

    segmenter = m21.analysis.segmentByRests.Segmenter().getSegmentsList

    def __init__(self, segment:list[Note], score_info:ScoreAnalysis):

        self.stream = Stream(segment)
        self.notes = segment
        self.pitches = Segment.make_pitch_grid(segment) # midi
        self.pitches_compensated = False

        segment_analysis = {
            'segment_first_note_pitch': self.notes[0].pitch.name,
            'segment_first_note_duration': self.notes[0].duration.type,
            'segment_first_note_octave': self.notes[0].pitch.octave,
            'segment_finalis_pitch': self.notes[-1].pitch.name,
            'segment_finalis_duration': self.notes[-1].duration.type,
            'segment_finalis_octave': self.notes[-1].pitch.octave,
            'segment_total_duration': self.stream.quarterLength
        }

        self.info = dict(score_info, **segment_analysis)
        # self.score_info:ScoreAnalysis = score_info

    @classmethod
    def getSegmentsList(cls, streams:list[Stream], score_info:list[dict], equal_length=True, append_last=True) -> list['Segment']:

        scores = zip(streams, score_info)

        segments = [Segment(segment, score_info) for stream, score_info in scores for segment in tqdm(cls.segmenter(stream), desc='segmenting score']

        if equal_length:
            '''
            Make all phrases equal in lengths
            – compensate by prolonging last pitch.
            '''
            longest = max(len(segment.pitches) for segment in segments)
            for segment in segments:
                last_element = segment.pitches[-1] if append_last else 0
                for i in range(longest - len(segment.pitches)):
                    segment.pitches.append(last_element)
                segment.pitches_compensated = True

            assert all(len(segment.pitches) == len(segments[0].pitches) for segment in segments)

        return segments

    @classmethod
    def make_pitch_grid(cls, segment:list[Note]) -> list:

        exploded_segment:list[float] = []

        for note in segment:
            for i in range(int(note.quarterLength*2)):
                exploded_segment.append(note.pitch.midi) # NOT IDEAL !

        return exploded_segment
