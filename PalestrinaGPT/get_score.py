from dataclasses import dataclass

import music21 as m21
from music21.stream import Score, Part
from music21.note import Note, Rest
import re


# class PalestrinaScore

@dataclass
class PartNote:
	id:str # name
	name:str
	note:str|Note


def decode_note(part_note:str) -> Note:

	if '(' not in part_note.note:
		part_note.note += '(8)' # VERY WRONG !!!

	if 'Rest' in part_note.note:
		part_note.note = part_note.note.replace('Rest', 'REST')

	print(part_note)

	pitch, remaining_duration = re.findall(r'<(.+)>\((.+)\)', part_note.note)[0]
	note = Note(pitch=pitch) if pitch != 'REST' else Rest(pitch=pitch)
	note.quarterLength = int(remaining_duration) / 2

	return note


def get_part(note:Note) -> Part:

	part = next(cs.site for cs in note.contextSites() if isinstance(cs.site, Part))
	return part


def get_score(score:str, all_voices=False) -> Score:

	m21score = Score()
	offset = 0

	if '\n' in score:
		score = score.replace('\n', '')

	simultaneities = score.split(';')

	for i, simultaneity in enumerate(simultaneities):

		if not simultaneity:
			continue

		part_notes = []

		if all_voices:

			print(simultaneity)
			part_notes = [PartNote(f'voiceName_{i}', *note_str.split('@')) for i, note_str in enumerate(reversed(simultaneity.split()))]

		else:

			if '?' not in simultaneity:
				print(f'Error line {i}: Wrong parsing.\n\t{simultaneity}')
				continue

			other_notes, voice_note = simultaneity.split('? ')
			other_notes = [PartNote(f'voiceName_{i}', *note_str.split('@')) for i, note_str in enumerate(reversed(other_notes.split()))]
			n_parts = len(other_notes)
			part_notes = other_notes + [PartNote(f'voiceName_{n_parts}', 'Voice', voice_note)]

		for n, part_note in enumerate(part_notes):

			part_note.note = decode_note(part_note)

			if i == 0:
				m21score.append(Part(id=part_note.id, partName=part_note.name))

		print(part_notes)

		shortest_quarterLength = min(part_note.note.quarterLength for part_note in part_notes)

		sounding_notes = {get_part(note).id : note
		                 for note in m21score.flatten().getElementsByOffset(offset, mustBeginInSpan=False)}

		'''Correct note duration and append notes to parts.'''
		for part_note in part_notes:
			
			if part_note.id in sounding_notes:

				part = next(part for part in m21score.parts if part.id == part_note.id)
				# print(sounding_notes[part_note.id].quarterLength, part_note.note.quarterLength, shortest_quarterLength)

				prev_note = sounding_notes[part_note.id]

				prev_note_pitch = prev_note.isRest or prev_note.pitch
				curr_note_pitch = part_note.note.isRest or part_note.note.pitch

				# relative_offset = prev_note.offset - part_note.note.quarterLength
				# relative_offset = prev_note.quarterLength - part_note.note.quarterLength
				# relative_offset = offset - prev_note.offset
				
				if prev_note_pitch != curr_note_pitch:
					# print(f'Error line {i}: Wrong parsing.\n\t{simultaneity}')

				# if (prev_note_pitch == curr_note_pitch) and (shortest_quarterLength != relative_offset):
				# 	...
				   print(f'Error line {i}: Wrong remaining durations')
				   print(f'\tPrev: {simultaneities[i-1]}\n\tCurr: {simultaneity}')
				   print(f'\t{part_note}')

				# else:
				# 	prev_note.tie = m21.tie.Tie('start')

			else:
				part = next(part for part in m21score.parts if part.id == part_note.id)
				part.insert(offset, part_note.note)


		offset += shortest_quarterLength


	return m21score






