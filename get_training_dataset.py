from pathlib import Path
from datasets import Dataset
from PalestrinaUTILS.scores.Score2TextConverter import Score2TextConverter

DATA_PATH = Path('PalestrinaDATA/training/')

converter1 = Score2TextConverter(
    resolve_chiavetta=True,
    include_part_name=True,
    repeat_tokens=True,
)

datadict, id = converter1.parse_database(n=2)
dataset = Dataset.from_dict(datadict)
print(dataset)
print(dataset['content'][0])
# dataset.save_to_disk(str(DATA_PATH/'dataset'/id))
