from __future__ import annotations
from transformations.transformation import Transformation

import transformations.text.utils.formality_change.styleformer as Styleformer
import torch

def set_seed(seed):
  torch.manual_seed(seed)
  if torch.cuda.is_available():
    torch.cuda.manual_seed_all(seed)

class CasualToFormal(Transformation):
    """
    Sentence transformation rule from the NL-Augmenter library
    "This transformation transfers text style from informal to formal"
    
    Code reference:  https://github.com/GEM-benchmark/NL-Augmenter/tree/main/nlaugmenter/transformations/formality_change
    """
    
    def __init__(self, max_outputs=-1):
        super().__init__(max_outputs=max_outputs)

    def generate(self, sentence: str):
        sf = Styleformer.Styleformer(style = 0) 
        set_seed(1212)
        results = sf.transfer(sentence, inference_on=-1, quality_filter=0.95, max_candidates=5)
        
        if results is None:
            return []
        else:
            return [results] if isinstance(results, str) is not None else results
