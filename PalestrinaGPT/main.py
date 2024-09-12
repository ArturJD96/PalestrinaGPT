import re
from random import randint, choice, shuffle
from dataclasses import dataclass

@dataclass
class Token:

	part:str
	pitch:str
	remaining_duration:int # in eight notes

	@classmethod
	def from_string(Self, string) -> 'Token':

		part, note_str = string.split('@')
		pitch = re.findall(r'<(.+)>', note_str)[0]
		remaining_duration = int(re.findall(r'\((.+)\)', string)[0]) or -1

		return Token(part, pitch, remaining_duration)

	def __str__(self) -> str:

		return f'{self.part}@<{self.pitch}>' + (f'({self.remaining_duration})' if self.remaining_duration > 0 else '')


@dataclass
class TokenLine:

	tokens:[Token]
	parts:[str]

	def ask_for(self, part:str, solved=False) -> (str, str):

		i = self.parts.index(part)
		this_part_token = self.tokens[i] # removed!
		other_parts_tokens = self.tokens[:i] + self.tokens[i+1:]

		other_parts = f'{' '.join(str(token) for token in other_parts_tokens)} ?'

		if solved:
			return ' '.join([other_parts, str(this_part_token).split('@')[1] + ';'])
		else:
			return other_parts

		# return f'{' '.join(str(token) for token in other_parts_tokens)} ?', this_part_token


	def empty(parts:[str]) -> 'TokenLine':
		return TokenLine([Token.from_string(f'{part}@<REST>(4)') for part in parts], parts)

	def from_string(string) -> 'TokenLine':
		parts = re.findall(r'(\w+)@', string)
		return TokenLine([Token.from_string(tok) for tok in string.split()], parts)

	def __str__(self):

		return ' '.join(str(token) for token in self.tokens)


@dataclass
class TokenScore:

	models:[]
	parts:[str]
	lines:[TokenLine]

	def choose_random_part() -> int:
		...

	def get(n) -> str:
		...

	def append(self) -> TokenLine:

		# line = TokenLine([None for i in range(len(self.models))])

		line = TokenLine.empty(self.parts)

		action_order = [i for i in range(len(self.models))]

		shuffle(action_order)

		for i in action_order:

			model = self.models[i]
			part:str = self.parts[i]
			part_line = line.ask_for(part)

			lines_and_results = [str(line.ask_for(part, solved=True)) for line in self.lines]
			# lines = [ for line, result in lines_and_results]

			lines = '\n'.join(lines_and_results + [part_line])
			result = model(lines) #, voices=len(models)+1)

			if '[UNK]' in result:
				break

			result = result.split('? ')[-1]
			note = f'{part}@{result}'.strip(';') if '@' not in result else result.strip(';')
			line.tokens[i] = note

		self.lines.append(line)


	def __str__(self):

		return ';\n'.join(str(line) for line in self.lines) + ';'


from transformers import pipeline, AutoModelForCausalLM

from palestrina_tokenizer import get_trained_palestrina_tokenizer
from get_score import get_score

@dataclass
class Model:

	model:...
	tokenizer:...
	new_tokens:int=1

	def __call__(self, text):

		inputs = self.tokenizer(text, return_tensors='pt')
		# outputs = self.model.generate(**inputs, temperature=0.9, max_new_tokens=(1+voices)) # max_length=512,
		outputs = self.model.generate(**inputs, do_sample=True, max_new_tokens=1) # max_length=512,
		# outputs = outputs[:, inputs.input_ids.shape[1]:]
		result = self.tokenizer.decode(outputs[0])

		return result


gpt = AutoModelForCausalLM.from_pretrained('output/checkpoint-102720', do_sample=True)
tokenizer = get_trained_palestrina_tokenizer()

model = Model(gpt, tokenizer)

# pipeline_args = dict(task='text-generation',
# 	                 model=path,
# 	                 tokenizer=tokenizer,
# 	                 device='mps',
# 	                 max_length=512,
# 	                 temperature = 0.5,
# 	                 max_new_tokens=512,
# 	                 truncation=True)

parts = ['Bass', 'Tenor', 'Alto', 'Soprano']
# lines = [TokenLine.empty(parts)]
lines = [TokenLine.from_string('Bass@<REST>(8) Tenor@<G3>(8) Alto@<REST>(8) Soprano@<REST>(8)')]
         #TokenLine.from_string('Bass@<REST>(8) Tenor@<D4>(8) Alto@<REST>(8) Soprano@<REST>(8)')]

models = [model for i in range(len(parts))]

score = TokenScore(models=models, parts=parts, lines=lines)

for i in range(50): score.append()

print(score)

sc = get_score(str(score), all_voices=True)

sc.show()
