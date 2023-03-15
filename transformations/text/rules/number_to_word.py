from __future__ import annotations
from transformations.transformation import Transformation

import inflect
import transformations.text.utils.text_helper as text_helper

"""
Verbalizing numbers of the text
"""

infEng = inflect.engine()

def word_to_number(text):
    results = []
    trans = []
    for token in text.split():
        if token.isdigit() and (not text_helper.is_protected(token, text)):
            words = infEng.number_to_words(int(token), wantlist=True)
            trans.extend(words)
        else:
            trans.append(token)
    results.append(" ".join(trans))
    return results


class NumberToWord(Transformation):
    """
    Sentence transformation rule from the NL-Augmenter library
    "This perturbation converts numbers of the text to their corresponding words."
    
    Code reference: https://github.com/GEM-benchmark/NL-Augmenter/tree/main/nlaugmenter/transformations/number-to-word
    """
    
    def __init__(self, max_outputs=-1):
        super().__init__(max_outputs=max_outputs)

    def generate(self, sentence: str):
        pertubed = word_to_number(text=sentence)
        return pertubed
