import yaml
from pathlib import Path
from datetime import datetime
from tqdm import tqdm

import numpy as np

import music21 as m21
from music21.stream.base import Stream, Score, Part
from music21.note import GeneralNote, Note, Rest
from music21.pitch import Pitch
from music21.duration import Duration

# from ScoreAnalyzer import ScoreAnalyzer
from PalestrinaUTILS.scores.ScoreAnalyzer import ScoreAnalyzer


class ScoreAsText(str):

    def save(self, path:Path, file_name:str) -> None:
        path.mkdir(parents=True, exist_ok=True)
        (path / f'{file_name}.txt').write_text(self)


class Score2TextConverter:

    data_path = Path('PalestrinaDATA/training/score_txt')

    rest_token = 'rest'
    repeat_token = '.'

    pitch_modes = { # n:Note
        'nameWithOctave': lambda n: n.nameWithOctave
    }

    duration_modes = { # d:Note, o:float (current offset)
        'remainingQuarterLength': lambda n, o: f'{n.offset + n.quarterLength - o}',
        'quarterLength': lambda n, o: f'{n.quarterLenght}',
        'fractionQuarterLength': lambda n, o: f'{n.quarterLength}:{n.offset + n.quarterLength - o}'
    }


    def __init__(self,
        shortest_offset:float=0.5, #quarterLength
        resolve_chiavetta=False,
        repeat_tokens:bool=False,
        include_part_name:bool=True,
        pitch_mode:str='nameWithOctave',
        duration_mode:str='remainingQuarterLength'):

        self.shortest_offset = shortest_offset
        self.resolve_chiavetta = resolve_chiavetta

        self.repeat_tokens = repeat_tokens
        self.include_part_name = include_part_name

        self.pitch_mode = pitch_mode
        self.duration_mode = duration_mode


    def __call__(self, score:Score) -> ScoreAsText:

        score_array:np.ndarray = self.score2array(score) # 2d: note, part.
        score_string:str = self.stringify_score_array(score_array)

        return ScoreAsText(score_string)


    def parse_database(self, m21composer='palestrina') -> tuple[dict, str]:

        dataset:dict = {
            'id':[],
            'metadata':[],
            'voice':[],
            'content':[]
        }

        id:str = str(datetime.now()).split('.')[0]
        analyzer = ScoreAnalyzer()

        metadata:dict = self.__dict__
        metadata['id'] = id

        for score_path in tqdm(m21.corpus.getComposer(m21composer), desc='Parsing'):

            score:Score = m21.converter.parse(score_path).stripTies() #type:ignore
            score_id = analyzer.get_id(score)

            if self.resolve_chiavetta: analyzer.resolve_chiavetta(score)

            score_text = self(score)
            dataset['id'].append(score_id)
            dataset['metadata'].append(metadata)
            dataset['voice'].append('all')
            dataset['content'].append(self(score))

        return dataset, id


    def parse_database_and_save(self, m21composer='palestrina') -> Path:

        id:str = str(datetime.now()).split('.')[0]
        path:Path = Score2TextConverter.data_path / id
        self.save_info(path=path)

        for score_path in tqdm(m21.corpus.getComposer(m21composer), desc='Parsing, analyzing, converting scores'):

            score:Score = m21.converter.parse(score_path).stripTies() #type:ignore

            analyzer = ScoreAnalyzer()
            score_id = analyzer.get_id(score)

            if self.resolve_chiavetta: analyzer.resolve_chiavetta(score)

            score_text = self(score)
            score_text.save(path=path, file_name=score_id)

        return path


    def save_info(self, path:Path) -> None:
        params = yaml.dump(self.__dict__)
        path.mkdir(parents=True, exist_ok=True)
        (path / f'converter_info.yaml').write_text(params)


    def get_part(self, note:GeneralNote) -> Part:

        sites:list = sorted([site for site,_,_ in note.contextSites() if isinstance(site, Part)], key=lambda p: p.id)
        # sites:list = sorted(set(site for site, _, _ in note.contextSites(returnSortTuples=True) if isinstance(site, Part)), key=lambda part: part.id)
        # print(note.getContextByClass(Part)) # why doesn't it work with sorted?
        assert len(sites) >= 1
        part:Part = sites[0]
        return part


    def score2array(self, score:Score) -> np.ndarray:

        general_notes = score.flatten().notesAndRests
        curr_offset, total_offset, prev_ids = 0, score.quarterLength, set()
        notes:list[list[GeneralNote]] = []

        while curr_offset < total_offset:

            '''Check if there are new notes in slice'''
            music_slice = list(general_notes.getElementsByOffset(curr_offset, mustBeginInSpan=False))
            curr_ids = set(general_note.id for general_note in music_slice)
            repeated_ids = curr_ids & prev_ids
            # if curr_ids == prev_ids:
            #     curr_offset += self.shortest_offset
            #     continue

            '''Sort slices by Part id (they don't get sorted automatically)'''
            music_slice = sorted(music_slice, key=lambda general_note: self.get_part(general_note).id)
            notes.append(music_slice)

            prev_ids = curr_ids
            curr_offset += self.shortest_offset

        return np.array(notes)

    # def remove_repeated_tokens(self, score:np.ndarray) -> np.ndarray:
    #     '''For each part...'''
    #     for part_id in range(score.shape[1]):
    #         '''...find how much the note is repeated...'''
    #         for c, curr_note in enumerate(score[:,part_id]):
    #             if curr_note == Scom`re2TextConverter.repeat_token:
    #                 continue
    #             '''...and remove repetitions.'''
    #             for n, next_note in enumerate(score[c+1:,part_id]):
    #                 if next_note.id != curr_note.id: break
    #                 score[c+n,part_id] = Score2TextConverter.repeat_token

    #     return score

    # def get_remaining_offset(self, general_note:GeneralNote):


    def stringify_score_array(self, score_array:np.ndarray) -> str:

        score_str = ''
        empty_line = ' '.join(Score2TextConverter.repeat_token for i in range(score_array.shape[1]))

        for i, simultaneity in enumerate(score_array):

            # shortest_lasting_note
            offset = self.shortest_offset * i
            line_str = ' '.join(self.stringify_note(note, offset) for note in simultaneity)
            if line_str == empty_line: continue
            score_str += line_str
            score_str += '\n'

        return score_str


    def stringify_note(self, general_note:GeneralNote, current_offset:float) -> str:

        string = ''

        if not self.repeat_tokens and (general_note.offset < current_offset):

            '''i.e. note starts earlier'''
            string = Score2TextConverter.repeat_token

        else:

            pitch = self.stringify_pitch(general_note)
            duration = self.stringify_duration(general_note, current_offset)
            string = f'<{pitch}>({duration})'

            if self.include_part_name:

                part_name:str = self.get_part(general_note).partName
                if part_name == 'Baritone': part_name = 'Bass'
                string = f'{part_name}@{string}'

        return string


    def stringify_pitch(self, general_note:GeneralNote) -> str:

        if general_note.isRest: return Score2TextConverter.rest_token

        note:Note = general_note #type: ignore

        return Score2TextConverter.pitch_modes[self.pitch_mode](note)


    def stringify_duration(self, general_note:GeneralNote, current_offset:float) -> str:

        return Score2TextConverter.duration_modes[self.duration_mode](general_note, current_offset)
