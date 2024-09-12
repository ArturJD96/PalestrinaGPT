from pathlib import Path
from datasets import Dataset

# TO DO: merge with 'make_data.py': cause it to output dataset immediately.

DATA_PATH = Path('PalestrinaDATA/training/score_txt/2024-09-10 23:07:29')

'''Save all datasets.'''

training_data = {
    'id': [],
    'content': [],
}

for score_txt_file in DATA_PATH.iterdir():

    if not score_txt_file.suffix == '.txt': continue

    training_data['id'].append(score_txt_file.stem)
    training_data['content'].append(score_txt_file.read_text())

dataset = Dataset.from_dict(training_data)
dataset.save_to_disk(str(DATA_PATH/'dataset'))
