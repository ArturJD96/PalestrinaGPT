from pathlib import Path
from datasets import Dataset
from PalestrinaUTILS.scores.Score2TextConverter import Score2TextConverter

DATA_PATH = Path('PalestrinaDATA/training/')

converter1 = Score2TextConverter(
    resolve_chiavetta=True,
    include_part_name=False
)

# converter1.parse_database_and_save() # saving directly to the disk as .txt files.

dataset_dict, id = converter1.parse_database()
dataset = Dataset.from_dict(dataset_dict)
dataset.save_to_disk(str(DATA_PATH/'dataset'/id))
