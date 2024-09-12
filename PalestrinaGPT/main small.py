from transformers import pipeline

from palestrina_tokenizer import get_trained_palestrina_tokenizer
from get_score import get_score

'''
This one works! The original one.
'''

path = 'output/checkpoint-102720'

tokenizer = get_trained_palestrina_tokenizer()

pipe = pipeline('text-generation',
	            model=path,
	            tokenizer=tokenizer,
	            device='mps',
	            max_length=512,
	            temperature = 99.0,
	            max_new_tokens=512)

# x = 'Bass@<REST>(8) Tenor@<G3>(8) Tenor@<G3>(8) Soprano@<REST>(8) ?'
# x = 'Bass@<REST>(8) Alto@<REST>(8) Soprano@<REST>(8) ?'
# x = 'Bass@<REST>(16) Tenor@<REST>(16) Alto@<REST>(16) Soprano@<REST>(8) ? <D4>(16); Bass@<REST>(8) Tenor@<REST>(8) Alto@<REST>(8) Soprano@<D5>(6) ?'
# x = '''
# Bass@<E3>(16) Tenor@<F3>(16) Alto@<G3>(16) ? ;
# Bass@<REST>(16) Tenor@<E3>(2) Alto@<REST>(16) ? <REST>(2);
# Bass@<REST>(16) Tenor@<F3>(4) Alto@<REST>(16) ? <D4>(6);
# Bass@<REST>(16) Tenor@<D3>(6) Alto@<REST>(16) ?
# '''
x = '''Bass@<E3>(1) Tenor@<F3>(6) Alto@<E-4>(1) ? <G4>(1);'''

score_str = pipe(x)[0]['generated_text']

print(score_str.replace(';', ';\n'))

score = get_score(score_str)

score.show()
