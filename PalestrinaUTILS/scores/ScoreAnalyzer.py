from pathlib import Path

import music21 as m21
from music21.stream.base import Stream, Score
from music21.pitch import Pitch


class ScoreAnalysis(dict):
    ...

class ScoreAnalyzer():

    DEFAULT_DATABASE = 'Palestrina'

    def __init__(self):
        ...

    def __call__(self, score:Score, database_name=None) -> ScoreAnalysis:

        analysis = ScoreAnalysis()

        database = database_name or ScoreAnalyzer.DEFAULT_DATABASE
        score_path = Path(score.metadata.filePath)
        '''
        Find basic information
        '''
        analysis['path'] = str(score_path)
        analysis['id'] = self.get_id(score)
        analysis['database'] = database
        analysis['composer'] = score.metadata.composer
        analysis['mass_title'] = score_path.stem.split('_')[0]
        analysis['ordinarium'] = score.metadata.title # bette
        analysis['section'] = score.metadata.title
        analysis['part_count'] = [True for part in score.parts if len(part.recurse().notes) > 0].count(True)
        analysis['total_note_count'] = len(score.flatten().notes)
        analysis['total_duration'] = score.quarterLength
        '''
        Find key signature related info
        '''
        key_signature = self.get_keySignature(score)
        scala = self.estimate_chiavetta(score, key_signature)

        score_chords:Score = score.chordify().flatten().notes #type:ignore
        first_lowest_pitch = score_chords.first().sortAscending().pitches[0]
        last_lowest_pitch = score_chords.last().sortAscending().pitches[0]

        analysis['opening_bass_note'] = first_lowest_pitch.name
        analysis['bass_finalis'] = last_lowest_pitch.name

        analysis['key_signature'] = key_signature
        analysis['scala'] = scala
        analysis['mode'] = self.get_mode(score, key_signature, scala, last_lowest_pitch)
        analysis['chiavetta'] = self.estimate_chiavetta(score, key_signature)

        return analysis


    def get_id(self, score:Score) -> str:

        return Path(score.metadata.filePath).stem


    def get_mode(self, score:Score, key_signature:str, scala:str, last_lowest_pitch:Pitch) -> str:

        modes = ['Ionian', 'Dorian', 'Phrygian', 'Lydian', 'Mixolydian', 'Aeolian', 'Locrian']

        is_ks_complex = ' ' in key_signature
        if is_ks_complex:
            return 'complex'
        elif scala == 'other':
            return 'other'
        else:
            index = last_lowest_pitch.diatonicNoteNum - 1
            finalis = (index + 4 if scala == 'bmollaris' else index) % 7
            mode = modes[finalis]
            return mode


    def get_keySignature(self, score:Score) -> str:
        '''
        Find key signature related info
        '''

        def get_ks(part) -> str:
            # Maybe can be done easier?
            ks = part.flatten().keySignature
            return str(ks.sharps) if ks else '0'

        part_ks = [get_ks(part) for part in score.parts]
        is_ks_simple = len(set(part_ks)) == 1
        key_signature = part_ks[0] if is_ks_simple else ' '.join(part_ks)

        return key_signature


    def get_scala(self, key_signature:str) -> str:

        scala = ...

        if key_signature == '0': scala = 'naturalis'
        elif key_signature == '-1': scala = 'bmollaris'
        else: scala = 'other'

        return scala


    def estimate_chiavetta(self, score:Score, key_signature:str|None=None) -> str:
        '''
        Find chiavetta (estimation!)
        NOTE: The Palestrina database does not record original clefs.
            Thus, I estimate the chiavetta by checking the:
            – highest note of the highest voice.
            – lowest note of the Bass voice.
        '''

        key_signature = key_signature or self.get_keySignature(score)

        def estimate_chiavetta(score:Score, lowest:str, highest:str) -> tuple[bool, bool]:

            ambitus = m21.analysis.discrete.Ambitus().getPitchSpan(score)

            assert ambitus

            check_top = (ambitus[1] >= Pitch(highest)) and (score.parts[0].partName == 'Soprano')
            check_low = (ambitus[0] >= Pitch(lowest)) and ((score.parts[-1].partName == 'Bass') or (score.parts[-1].partName == 'Baritone'))

            return check_low, check_top

        expected_ambitus = ['Bb2', 'F'] if int(key_signature) < 0 else ['C3', 'G5']
        low, top = estimate_chiavetta(score, *expected_ambitus)

        chiavetta = 'high' if (low or top) else 'low'

        return chiavetta


    def resolve_chiavetta(self, score:Score, chiavetta:str|None=None, scala:str|None=None, inPlace=True):

        if scala == 'other': return score

        if not chiavetta:

            chiavetta = self.estimate_chiavetta(score)

        if not scala:

            key_signature = self.get_keySignature(score)
            scala = self.get_scala(key_signature)

        if chiavetta == 'high':

            interval:int = -5 if scala == 'bmollaris' else -7
            score.transpose(interval, inPlace=inPlace)

        return score
