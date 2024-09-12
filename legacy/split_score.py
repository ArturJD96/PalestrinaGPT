import music21 as m21
from music21.stream.base import Score as m21Score, Part as m21Part, Opus as m21Opus
from music21.note import GeneralNote as m21GNote

class NoteStringifier:

    rest_token = 'REST'

    def __init__(self, pitch_mode:str, duration_mode:str, repeated_notes:bool):

        self.pitch_mode = pitch_mode
        self.duration_mode = duration_mode
        self.repeated_notes = repeated_notes

    def __call__(self, note:'PartNote') -> str:

        # pitch
        pitch = NoteStringifier.rest_token if note.m21generalNote.isRest else note.m21generalNote.pitch.nameWithOctave
        # duration
        begin_offset = note.m21generalNote.offset
        current_offset = note.offset
        note_duration = note.m21generalNote.duration.quarterLength
        remaining_duration = begin_offset + note_duration - current_offset
        # convert float to int if no decimals are present
        if remaining_duration == int(remaining_duration):
            remaining_duration = int(remaining_duration)
        if note_duration == int(note_duration):
            note_duration = int(note_duration)
        # stringified info
        return f'<{pitch}>({str(remaining_duration)}/{note_duration})'


class PartNote:

    rest_token = 'REST'

    def __init__(self, note:m21GNote, offset:float):
        self.m21generalNote:m21GNote = note
        self.m21part:m21Part = self.get_part(note)
        self.offset = offset
        self.syllable = ...
        self.stringify:NoteStringifier = NoteStringifier(
            pitch_mode='pitchWithOctave',
            duration_mode='remainingQuarterLength',
            repeated_notes=True
        )

    def get_part(self, note:m21GNote) -> m21Part:
       	part = next(cs.site for cs in note.contextSites() if isinstance(cs.site, m21Part))
       	return part

    def __str__(self) -> str:
        return self.stringify(self)

    def __repr__(self) -> str:
        return "ARTUR!!! Write Stringifying function for PartNote!"

class ScorePart(list):
    def __init__(self, part:m21Part):
        self.m21part:m21Part = part
        self.id:str = int(str(part.id).split('_')[1]) # rewrite with regex match
        self.voice:str = part.partName
        self.notes = []

class ScoreManager:

    def __init__(self, score:m21Score):
        self.m21score:m21Score = score
        self.parts:list[ScorePart] = self.make_parts()
        self.dispose_notes_to_parts()

    def make_parts(self) -> list:
        parts = [ScorePart(m21part) for m21part in self.m21score.parts]
        parts.sort(key = lambda part: part.id)
        return parts

    def dispose_notes_to_parts(self) -> None:
        notes_and_rests = self.m21score.flatten().notesAndRests
        prev_ids = []
        for quaver in range(int(score.quarterLength * 2)):
            offset = quaver / 2
            events = notes_and_rests.getElementsByOffset(offset, mustBeginInSpan=False)
            ids = set(event.id for event in events)
            # NOTE: make rests not counting in this comparison!!??
            if ids != prev_ids:
                for event in events:
                    note = PartNote(event, offset)
                    id = int(str(note.m21part.id).split('_')[1]) # rewrite!
                    self.parts[id].append(note)
            prev_ids = ids

    def stringify(self) -> str:
        string = ''
        for simultaneous_notes in zip(*reversed(self.parts)):
            string += ' '.join(str(note) for note in simultaneous_notes) + '\n'
        # return "ARTUR!!! Write Stringifying function for CustomScore!"
        return string

    def __str__(self) -> str:
        return self.stringify()

    def __repr__(self) -> str:
        return self.stringify()


'''
Hmmm...
I have 'ScoreManager' and 'PartNote'
I have 'ScoreStringifier'

Maybe make 'NoteStringifier'?
'''

# PartNote.stringify = PartNoteStringifier()

score:m21Score = m21.corpus.parse('palestrina')
print(ScoreManager(score))
