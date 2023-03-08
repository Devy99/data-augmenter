from __future__ import annotations
from transformations.transformation import Transformation

import os, json
import transformations.text.utils.initialize as spacy_nlp
import transformations.text.utils.text_helper as text_helper

class CorrectCommonMisspellings(Transformation):

    def __init__(self, seed=0, max_outputs=-1):
        super().__init__(seed, max_outputs=max_outputs)
        self.COMMON_MISSPELLINGS_DICT = get_common_misspellings_dict()
        self.nlp = spacy_nlp.spacy_nlp

    def generate(self, sentence: str):
        doc = self.nlp(sentence)
        
        tokens = []
        for token in doc:
            t = token.text
            if not text_helper.is_protected(token.text, sentence):
                t = self.COMMON_MISSPELLINGS_DICT.get(token.text, token.text) 
                
            if token.whitespace_: t += " "
            tokens.append(t)
        """
        perturbed_text = [
            self.COMMON_MISSPELLINGS_DICT.get(token.text, token.text) + " "
            if token.whitespace_
            else self.COMMON_MISSPELLINGS_DICT.get(token.text, token.text)
            for token in doc
        ]
        """
        return ["".join(tokens)]


def get_common_misspellings_dict():
    
    spell_corrections = os.path.join(
        'transformations','text','utils','correct_common_misspellings', 'spell_corrections.json'
        )
    with open(spell_corrections, "r") as fp:
        spell_corrections = json.load(fp)
    return spell_corrections
