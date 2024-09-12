from pathlib import Path

import wandb

from PalestrinaGPT.palestrina_tokenizer import get_trained_palestrina_tokenizer

DATA_PATH = Path('PalestrinaDATA/training/score_txt/2024-09-10 23:07:29/dataset')
tokenizer = get_trained_palestrina_tokenizer(str(DATA_PATH))

from datasets import Dataset

# Download dataset - you can change it for your own dataset
ds = Dataset.load_from_disk(str(DATA_PATH))

raw_datasets = ds.train_test_split(test_size=0.1, shuffle=True)

context_length = 2048

'''
Tokenize dataset
'''
def tokenize(element):
  outputs = tokenizer(
      element["content"],
      truncation=True, #Removing element longer that context size, no effect in JSB
      max_length=context_length,
      padding=False
  )
  return {"input_ids": outputs["input_ids"]}

tokenized_datasets = raw_datasets.map(tokenize,
                                      batched=True,
                                      remove_columns=raw_datasets["train"].column_names)


# ~ ~ ~ ~ ~ ~ ~ ~ ~ https://huggingface.co/blog/juancopi81/using-hugging-face-to-train-a-gpt-2-model-for-musi

# # # # # # # # # #
#  MODEL CONFIG   #
# # # # # # # # # #
from transformers import AutoConfig, GPT2LMHeadModel
'''
Change this based on size of the data
'''
n_layer=6 # Number of transformer layers
n_head=8 # Number of multi-head attention heads
n_emb=512 # Embedding size

config = AutoConfig.from_pretrained(
    "gpt2",
    vocab_size=len(tokenizer),
    n_positions=context_length,
    n_layer=n_layer,
    n_head=n_head,
    pad_token_id=tokenizer.pad_token_id,
    bos_token_id=tokenizer.bos_token_id,
    eos_token_id=tokenizer.eos_token_id,
    n_embd=n_emb
)

model = GPT2LMHeadModel(config)

# # # # # # # # # #
#  DATA COLLATOR  #
# # # # # # # # # #
from transformers import DataCollatorForLanguageModeling
'''
It supports both masked language modeling (MLM) and causal language modeling (CLM)
We need to set mlm=False for CLM
'''
data_collator = DataCollatorForLanguageModeling(tokenizer, mlm=False)


from transformers import Trainer, TrainingArguments
'''
first create a custom trainer to log prediction distribution
'''
# SAMPLE_RATE=44100

# class CustomTrainer(Trainer):

#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)

    # def evaluation_loop(self, dataloader, description,
    #                     prediction_loss_only=None,
    #                     ignore_keys=None,
    #                     metric_key_prefix="eval"):

    #     # call super class method to get the eval outputs
    #     eval_output = super().evaluation_loop(
    #         dataloader,
    #         description,
    #         prediction_loss_only,
    #         ignore_keys,
    #         metric_key_prefix,
    #     )

    #     # log the prediction distribution using `wandb.Histogram` method.
    #     if wandb.run is not None:

    #         input_ids = tokenizer.encode("Bass@<C3>(16) Tenor@<G3>(8) Tenor@<C4>(6) Soprano@<E4>(8) ?", return_tensors="pt").mps()
    #         '''
    #         Generate more tokens.
    #         '''
    #         voice1_generated_ids = model.generate(
    #             input_ids,
    #             max_length=512,
    #             do_sample=True,
    #             temperature=0.75,
    #             eos_token_id=tokenizer.encode("Soprano@<E4>(8)")[0]
    #         )
    #         # voice2_generated_ids = model.generate(
    #         #     voice1_generated_ids,
    #         #     max_length=512,
    #         #     do_sample=True,
    #         #     temperature=0.75,
    #         #     eos_token_id=tokenizer.encode("Tenor@<C4>(6)")[0]
    #         # )
    #         # voice3_generated_ids = model.generate(
    #         #     voice2_generated_ids,
    #         #     max_length=512,
    #         #     do_sample=True,
    #         #     temperature=0.75,
    #         #     eos_token_id=tokenizer.encode("Tenor@<G3>(8)")[0]
    #         # )
    #         # voice4_generated_ids = model.generate(
    #         #     voice3_generated_ids,
    #         #     max_length=512,
    #         #     do_sample=True,
    #         #     temperature=0.75,
    #         #     eos_token_id=tokenizer.encode("TRACK_END")[0]
    #         # )

    #         # token_sequence = tokenizer.decode(voice4_generated_ids[0])
    #         token_sequence = tokenizer.decode(voice1_generated_ids[0])
    #         # note_sequence = token_sequence_to_note_sequence(token_sequence)
    #         # synth = note_seq.fluidsynth
    #         # array_of_floats = synth(note_sequence, sample_rate=SAMPLE_RATE)
    #         # int16_data = note_seq.audio_io.float_samples_to_int16(array_of_floats)
    #         # wandb.log({"Generated_audio": wandb.Audio(int16_data, SAMPLE_RATE)})
    #         wandb.log({'Generated_text': token_sequence})

    #     return eval_output


# # # # # # # # # #
# START TRAINING  #
# # # # # # # # # #

'''
Create the args for out trainer
'''
from argparse import Namespace
'''
Get the output directory with timestamp.
'''
output_path = "output" # 'PalestrinaGPT/output'
steps = 5000
'''
Commented parameters
'''
config = {"output_dir": output_path,
          "num_train_epochs": 20,
          "per_device_train_batch_size": 8,
          "per_device_eval_batch_size": 4,
          "evaluation_strategy": "steps",
          "save_strategy": "steps",
          "eval_steps": steps,
          "logging_steps":steps,
          "logging_first_step": True,
          "save_total_limit": 5,
          "save_steps": steps,
          "lr_scheduler_type": "cosine",
          "learning_rate":5e-4,
          "warmup_ratio": 0.01,
          "weight_decay": 0.01,
          "seed": 1,
          "load_best_model_at_end": True,
          "report_to": "wandb"}

args = Namespace(**config)

train_args = TrainingArguments(**config)
'''
Use the CustomTrainer created above
[AJD:] using the default one.
'''
trainer = Trainer(
    model=model,
    tokenizer=tokenizer,
    args=train_args,
    data_collator=data_collator,
    train_dataset=tokenized_datasets["train"],
    eval_dataset=tokenized_datasets["test"],
)
'''
Train the model.
'''
trainer.train() #resume_from_checkpoint=True
