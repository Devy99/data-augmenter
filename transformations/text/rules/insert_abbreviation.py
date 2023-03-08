from __future__ import annotations
from transformations.transformation import Transformation
from pathlib import Path
        
import os
import transformations.text.utils.text_helper as text_helper
import transformations.text.utils.insert_abbreviation.grammaire as grammaire

def readfile(file):
    with open(file, encoding="utf8") as input:
        lines = input.readlines()
    return lines


def load_rules(file):
    with open(file, encoding="utf8") as input:
        str_rules = input.read()
    return str_rules


"""
Abbreviations
"""

class InsertAbbreviation(Transformation):
    """
    Sentence transformation rule from the NL-Augmenter library
    "This replacement adds noise to all types of text sources (sentence, paragraph, etc.) according to a rule system that encodes word sequences associated with their replacement label"
    
    Code reference: https://github.com/GEM-benchmark/NL-Augmenter/tree/main/nlaugmenter/transformations/insert_abbreviation
    """
    
    def __init__(self, seed=0, max_outputs=-1):
        
        text_path = os.path.realpath(__file__).replace(
            os.path.basename(__file__), ""
        )
        rulefile_en = os.path.join(Path(text_path).parents[0], "utils", "insert_abbreviation", "replacement_rules_en.txt")
        
        super().__init__(seed, max_outputs=max_outputs)
        rules_en = load_rules(rulefile_en)
        # First we compile our rules...
        self.grammar_en = grammaire.compile(rules_en)
        
    def generate(self, sentence: str):
        results = grammaire.parse(sentence, self.grammar_en)
        # We now replace the strings with their label
        perturbed_texts = sentence
        # Each list in results is an element such as: [label, [left,right]]
        # label pertains from rules
        # left is the left offset of the isolated sequence of words
        # right is the right offset of the isolated sequence of words
        # elements are stored from last to first in the text along the offsets
        for v in results:
            from_token = v[1][0]
            to_token = v[1][1]
            if not text_helper.is_protected(v[0], sentence):
                perturbed_texts = (
                    perturbed_texts[:from_token]
                    + v[0]
                    + perturbed_texts[to_token:]
                )
        return [perturbed_texts]
