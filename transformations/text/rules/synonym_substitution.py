﻿from __future__ import annotations
from transformations.transformation import Transformation
from nltk.corpus import wordnet
from spacy.cli.download import download

import re
import nltk
import numpy as np
import spacy
import transformations.text.utils.lexical_counterfactual_generator.initialize as spacy_nlp

"""
Base Class for implementing the different input transformations a generation should be robust against.
"""

def untokenize(words):
    """
    Untokenizing a text undoes the tokenizing operation, restoring
    punctuation and spaces to the places that people expect them to be.
    Ideally, `untokenize(tokenize(text))` should be identical to `text`,
    except for line breaks.
    ref: https://github.com/commonsense/metanl/blob/master/metanl/token_utils.py#L28
    """
    text = " ".join(words)
    step1 = (
        text.replace("`` ", '"').replace(" ''", '"').replace(". . .", "...")
    )
    step2 = step1.replace(" ( ", " (").replace(" ) ", ") ")
    step3 = re.sub(r' ([.,:;?!%]+)([ \'"`])', r"\1\2", step2)
    step4 = re.sub(r" ([.,:;?!%]+)$", r"\1", step3)
    step5 = (
        step4.replace(" '", "'")
        .replace(" n't", "n't")
        .replace("can not", "cannot")
    )
    step6 = step5.replace(" ` ", " '")
    return step6.strip()


def synonym_substitution(
    text, spacy_pipeline, seed=42, prob=0.5, max_outputs=1
):
    np.random.seed(seed)
    upos_wn_dict = {
        "VERB": "v",
        "NOUN": "n",
        "ADV": "r",
        "ADJ": "s",
    }

    doc = spacy_pipeline(text)
    results = []
    for _ in range(max_outputs):
        result = []
        for token in doc:
            word = token.text
            wn_pos = upos_wn_dict.get(token.pos_)
            if wn_pos is None:
                result.append(word)
            else:
                syns = wordnet.synsets(word, pos=wn_pos)
                syns = [syn.name().split(".")[0] for syn in syns]
                syns = [syn for syn in syns if syn.lower() != word.lower()]
                if len(syns) > 0 and np.random.random() < prob:
                    result.append(np.random.choice(syns).replace("_", " "))
                else:
                    result.append(word)

        # detokenize sentences
        result = untokenize(result)
        if result not in results:
            # make sure there is no dup in results
            results.append(result)
    return results


class SynonymSubstitution(Transformation):
    """
    Sentence transformation rule from the NL-Augmenter library
    "Substitute words with synonyms using stanza (for POS) and wordnet via nltk (for synonyms)"
    
    Code reference: https://github.com/GEM-benchmark/NL-Augmenter/tree/main/nlaugmenter/transformations/synonym_substitution
    """
    
    def __init__(self, seed=42, prob=0.5, max_outputs=-1):
        super().__init__(seed, max_outputs=max_outputs)
        
        try:
            self.nlp = spacy_nlp.spacy_nlp if spacy_nlp.spacy_nlp else spacy.load("en_core_web_sm")
        except Exception as e:
            download(model="en_core_web_sm")
            self.nlp = spacy_nlp.spacy_nlp if spacy_nlp.spacy_nlp else spacy.load("en_core_web_sm")

        self.prob = prob
        
        # Download only if the resource does not exist
        try:
            nltk.data.find('corpora/wordnet')
        except LookupError:
            nltk.download("wordnet", quiet=True)


    def generate(self, sentence: str):
        perturbed = synonym_substitution(
            text=sentence,
            spacy_pipeline=self.nlp,
            seed=self.seed,
            prob=self.prob,
            max_outputs=self.max_outputs,
        )
        return perturbed
