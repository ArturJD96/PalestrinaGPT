from pathlib import Path
from dataclasses import dataclass

from tqdm import tqdm
from tqdm.contrib import tenumerate

import music21 as m21
from music21 import Music21Object
from music21.stream import Stream, Score, Part
from music21.note import Note

from datasets import Dataset, concatenate_datasets


get_segments = m21.analysis.segmentByRests.Segmenter().getSegmentsList


def get_site(m21obj:Music21Object, m21class:type) -> Stream:
	
	site = next(cs.site for cs in m21obj.contextSites() if isinstance(cs.site, m21class))
	return site


def calc_remaining_quarterLength(note:Note, offset_curr:float) -> int:

	length_remaining = int((note.quarterLength - (offset_curr - note.offset)) * 2)
	return length_remaining


@dataclass
class NoteInfo:

	part:Part
	note:Note
	remaining_eights:int # instead of m21 Quarter Length: 8th note is Palestrina's shortest in this database (Masses).

	def __str__(self):

		if self.note.isNote:
			return f'<{self.note.nameWithOctave}>({self.remaining_eights})'
		elif self.note.isRest:
			return f'<REST>({self.remaining_eights})'


def segment2simultaneities(part:Part, segment:list[Note]) -> list[tuple[list[NoteInfo],NoteInfo]]:

	start_offset = segment[0].offset
	stop_offset  = segment[-1].offset + segment[-1].quarterLength

	score = get_site(part, Score)
	snippet = score.flatten().getElementsByOffset(start_offset, offsetEnd=stop_offset, mustBeginInSpan=False)

	simultaneities = []
	curr_offset = -1

	for note in snippet.notesAndRests:

		if note.offset == curr_offset:
			continue

		simultaneous_notes = snippet.getElementsByOffset(note.offset, mustBeginInSpan=False).notesAndRests

		simultaneous_notes = [NoteInfo(get_site(s_note, Part), s_note, calc_remaining_quarterLength(s_note, note.offset))
		                      for s_note in simultaneous_notes]

		simultaneous_notes = sorted(simultaneous_notes, key=lambda note_info: int(note_info.part.id.split('_')[1]))                  

		this_i = None
		for i, note_info in enumerate(simultaneous_notes):
			if note_info.part.id == part.id:
				this_i = i

		this_part_note = None
		other_part_notes = []
		if this_i is not None:
			this_part_note = simultaneous_notes[this_i]
			other_part_notes = simultaneous_notes[:this_i] + simultaneous_notes[this_i+1:]
		else:
			other_part_notes = simultaneous_notes

		simultaneities.append((other_part_notes, this_part_note))

		curr_offset = note.offset

	return simultaneities


def encode(simultaneity:tuple[list[NoteInfo],NoteInfo]) -> str:

	part_note = simultaneity[1]

	part_note_encoding = str(part_note) if part_note else '<REST>'
	other_notes_encoding = ' '.join(f'{note.part.partName}@{str(note)}' for note in simultaneity[0])

	return f'{other_notes_encoding} ? {part_note_encoding};'


if __name__ == '__main__':

	encoding  = 'letter_remainingDuration'
	encodings_path = Path('encodings') / encoding
	dataset_path = Path('datasets') / encoding

	encodings_path.mkdir(parents=True, exist_ok=True)
	dataset_path.mkdir(parents=True, exist_ok=True)

	score_paths = m21.corpus.getComposer('palestrina')

	scores = [ m21.corpus.parse(path) for path in tqdm(score_paths, desc='Importing Music21 scores') ]
	parts = [ part for score in scores for part in score.parts ]
	simultaneities = [(segment2simultaneities(part, segment), part) for part in tqdm(parts, desc='Calculating parts\' simultaneities') for segment in get_segments(part.flatten())]


	'''Slice scores to segments and encode them'''

	segments:dict = {} # by voice

	for i, (segment, part) in tenumerate(simultaneities, desc='Encoding simultaneities'):

		part_name = part.partName

		if part_name not in segments:
			segments[part_name] = []

		segment_encoded = '\n'.join(encode(simultaneity) for simultaneity in segment)

		segments[part_name].append(segment_encoded)

		(encodings_path / f'{part_name}_segment_{i}.txt').write_text(segment_encoded)


	'''Save all datasets.'''

	datasets = {}

	for part_name, part_segments in segments.items():

		voice_data = {
			'voice': [part_name for i in range(len(part_segments))],
			'id': [i for i in range(len(part_segments))],
			'content': [''.join(phrase) for phrase in part_segments]
		}

		dataset = Dataset.from_dict(voice_data)#.train_test_split()
		datasets[part_name] = dataset

	datasets['ALL'] = concatenate_datasets(list(datasets.values()))

	for name, dataset in datasets.items():
		dataset.save_to_disk(str(dataset_path / name))