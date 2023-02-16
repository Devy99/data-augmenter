from __future__ import annotations
from typing import List, Tuple
from transformations.transformation import Transformation
from transformers import M2M100ForConditionalGeneration, M2M100Tokenizer
from utils import cache_helper


def translate(sentence, src_lang, target_lang, model, tokenizer):
    tokenizer.src_lang = src_lang
    encoded_source_sentence = tokenizer(sentence, return_tensors="pt")
    generated_target_tokens = model.generate(
        **encoded_source_sentence,
        forced_bos_token_id=tokenizer.get_lang_id(target_lang)
    )
    target_sentence = tokenizer.batch_decode(
        generated_target_tokens, skip_special_tokens=True
    )
    return target_sentence


class MultilingualBackTranslation(Transformation):
    """
    Sentence transformation rule from the NL-Augmenter library
    "Translate a sentence to a pivot language and then back to the source lagnuage generating paraphrases.
    Can be used to do "Direct Trranslation" from a source language to itself."
    
    Code reference:https://github.com/GEM-benchmark/NL-Augmenter/tree/main/nlaugmenter/transformations/multilingual_back_translation
    """
    
    def __init__(
        self,
        seed=0,
        max_outputs=-1,
        src_lang: str = "en",
        pivot_lang: str = "zh",
    ):
        super().__init__(seed, max_outputs=max_outputs)
        
        model = cache_helper.get_file("facebook-m2m100_418M-model")
        if model is None:
            model = M2M100ForConditionalGeneration.from_pretrained("facebook/m2m100_418M")
            cache_helper.add_file(model, "facebook-m2m100_418M-model")
            
        tokenizer = cache_helper.get_file("facebook-m2m100_418M-tokenizer")
        if tokenizer is None:
            tokenizer = M2M100Tokenizer.from_pretrained("facebook/m2m100_418M")
            cache_helper.add_file(tokenizer, "facebook-m2m100_418M-tokenizer")
        
        self.model = model
        self.tokenizer = tokenizer
        
        self.src_lang = src_lang
        self.pivot_lang = pivot_lang

    def generate(self, sentence: str):

        # Source to Pivot
        pivot_sentence = translate(
            sentence,
            self.src_lang,
            self.pivot_lang,
            self.model,
            self.tokenizer,
        )

        # Pivot to Source
        if self.pivot_lang != self.src_lang:
            source_sentence = translate(
                pivot_sentence,
                self.pivot_lang,
                self.src_lang,
                self.model,
                self.tokenizer,
            )
        else:
            source_sentence = pivot_sentence

        return source_sentence

