from __future__ import annotations
from transformations.transformation import Transformation
from nltk.corpus import wordnet
from utils.threading_helper import synchronized

import re, numpy as np
import transformations.text.utils.initialize as spacy_nlp
import transformations.text.utils.text_helper as text_helper

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
        step4
        .replace(" n't", "n't")
        .replace(" 'm", "'m")
        .replace(" 's", "'s")
        .replace(" 're", "'re")
        .replace(" 've", "'ve")
        .replace("can not", "cannot")
    )
    
    step6 = step5
    items = text_helper.find_quotations(step6)
    for quotation in items:
        step6 = step6.replace(quotation, quotation.strip())
    
    step7 = step6.replace(" ` ", " '")
    return step7.strip()

@synchronized
def get_synsets(word: str, pos: str):
    return wordnet.synsets(word, pos=pos)

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
            if text_helper.is_protected(word, text):
                result.append(word)
                continue
            
            wn_pos = upos_wn_dict.get(token.pos_)
            if wn_pos is None:
                result.append(word)
            else:
                syns = get_synsets(word, wn_pos)
                syns = [syn.name().split(".")[0] for syn in syns]
                syns = [syn for syn in syns if syn.lower() != word.lower()]
                if len(syns) > 0 and np.random.random() < prob:
                    result.append(np.random.choice(syns).replace("_", " "))
                else:
                    result.append(word)

        # detokenize sentences
        result = untokenize(result)
        
        # Check result without whitespaces
        text_nows = ''.join(text.split())
        result_nows = ''.join(result.split())
        
        if result not in results and result_nows != text_nows:
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
        
        self.nlp = spacy_nlp.spacy_nlp
        self.prob = prob
        if max_outputs == -1: self.max_outputs = 10
        

    def generate(self, sentence: str):
        perturbed = synonym_substitution(
            text=sentence,
            spacy_pipeline=self.nlp,
            seed=self.seed,
            prob=self.prob,
            max_outputs=self.max_outputs,
        )
        return perturbed
