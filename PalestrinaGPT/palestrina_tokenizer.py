import pathlib as p

from datasets import Dataset, concatenate_datasets
from transformers import PreTrainedTokenizerFast
from tokenizers import Tokenizer, Regex, NormalizedString, PreTokenizedString, pre_tokenizers, models, processors, trainers


# class PalestrinaPreTokenizer():

#     # Creating custom pretokenizer:
#     # https://github.com/huggingface/tokenizers/blob/b24a2fc1781d5da4e6ebcd3ecb5b91edffc0a05f/bindings/python/examples/custom_components.py

#     pad_token = '[PAD]',
#     bos_token = '[BOS]',
#     eos_token = '[EOS]',
#     unk_token = '[UNK]',
#     sep_token = '[SEP]',
#     cls_token = '[CLS]',
#     mask_token = '[MASK]',

#     def split_commas(self, i:int, normalized_string: NormalizedString) -> list[NormalizedString]:
#         pattern = Regex(r',')
#         return normalized_string.split(pattern, 'removed')

#     def split_semicolon(self, i:int, normalized_string: NormalizedString) -> list[NormalizedString]:
#         pattern = Regex(r';')
#         return normalized_string.split(pattern, 'merged_with_previous')

#     def split_dot(self, i:int, normalized_string: NormalizedString) -> list[NormalizedString]:
#         pattern = Regex(r'\.')
#         return normalized_string.split(pattern, 'merged_with_next')

#     def pre_tokenize(self, pretok:PreTokenizedString):
#         pretok.split(self.split_commas)
#         pretok.split(self.split_semicolon)
#         pretok.split(self.split_dot)


def get_palestrina_tokenizer(training_data) -> PreTrainedTokenizerFast:

    # based mainly on dummy-tokenizer-wordlevel:
    # https://huggingface.co/robot-test/dummy-tokenizer-wordlevel

    special_tokens = {
        'pad_token': '[PAD]',
        'bos_token': '[BOS]',
        'eos_token': '[EOS]',
        'unk_token': '[UNK]',
        'sep_token': '[SEP]',
        'cls_token': '[CLS]',
        'mask_token': '[MASK]',
    }
    special_tokens_as_list = list(special_tokens.values())

    # pre_tokenizer = pre_tokenizers.PreTokenizer.custom(palestrina_pretokenizer())

    tokenizer = Tokenizer(models.WordLevel(unk_token='[UNK]'))

    tokenizer.add_special_tokens(special_tokens_as_list)
    tokenizer.pad_token_id = tokenizer.token_to_id('[PAD]')
    tokenizer.cls_token_id = tokenizer.token_to_id('[CLS]')
    tokenizer.sep_token_id = tokenizer.token_to_id('[SEP]')

    # tokenizer.pre_tokenizer = pre_tokenizer #pre_tokenizers.Whitespace() # dummy, replaced later.
    tokenizer.pre_tokenizer = pre_tokenizers.WhitespaceSplit() # dummy, replaced later.

    # tokenizer.post_processor = processors.TemplateProcessing(
    #     single=f"[CLS]:0 $A:0 [SEP]:0",
    #     pair=f"[CLS]:0 $A:0 [SEP]:0 $B:1 [SEP]:1",
    #     special_tokens=[("[CLS]", tokenizer.cls_token_id), ("[SEP]", tokenizer.sep_token_id)],
    # )

    trainer = trainers.WordLevelTrainer(vocab_size=50000, special_tokens=special_tokens_as_list)

    tokenizer.train_from_iterator(training_data, trainer=trainer)

    # https://github.com/huggingface/transformers/issues/11722
    # tokenizer.pre_tokenizer = pre_tokenizers.Whitespace() # dummy, replaced back after loading.

    tokenizer = PreTrainedTokenizerFast(
        tokenizer_file="PalestrinaTokenizer.json",
        tokenizer_object=tokenizer,
        bos_token="[CLS]",
        eos_token="[SEP]",
        unk_token="[UNK]",
        sep_token="[SEP]",
        pad_token="[PAD]",
        cls_token= "[CLS]",
        mask_token="[MASK]",
        # model_max_length=10,
        min_frequency=1,
        continuing_subword_prefix='##',
        padding_side="right"
    )

    # tokenizer._tokenizer.pre_tokenizer = pre_tokenizer # original pretokenizer.

    return tokenizer


def get_trained_palestrina_tokenizer(data_path:str='palestrina_data/datasets/letter_remainingDuration/ALL') -> ...:

    dataset = Dataset.load_from_disk(data_path)
    tokenizer = get_palestrina_tokenizer(dataset['content'])

    return tokenizer



if __name__ == '__main__':

    tokenizer = get_trained_palestrina_tokenizer()

    print(tokenizer)
    print(tokenizer.get_vocab())
    print(len(tokenizer))
