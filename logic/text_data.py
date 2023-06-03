from __future__ import annotations
from logic.data import Data
from utils.augment_helper import TransformedData, get_class
from transformations.text.text_generator import TextGenerator

import pandas as pd
import transformations.text.utils.text_helper as text_helper

class TextData(Data):
    """
    Specialization of the 'Data' class that takes as input only textual data 
    """
    
    def __init__(self, filepath: str, config: dict, verbose=False):
        super().__init__(filepath, config, verbose)
        text_helper.preserve_text = config['preserve-text']

    def augment(self, chunk: pd.DataFrame) -> pd.DataFrame:
        results = set()
        
        # Retrieve data from the dataframe chunk 
        snt_col = chunk[chunk.columns[self._data_column]]
        sentences = snt_col.values.tolist()
        
        # Retrieve available generator rules
        generator = TextGenerator()
        self._active_rules = list(set(self._active_rules) & set(generator.available_rules))
        
        for sid, sentence in enumerate(sentences):
            trs_id = chunk.index.values[sid]
            results.add(TransformedData(trs_id, sentence, 'original'))
            if self._max_outputs == 1 : continue
            
            for rule in self._active_rules:
                # Apply transformation
                cname = ''.join([ele.capitalize() for ele in rule.split('_')])
                generator.rule = get_class(generator.RULES_PACKAGE + rule + '.' + cname)(max_outputs=self._outputs_per_rule)
                transformations = generator.run(sentence)
                    
                transformations = [item for item in transformations if item != sentence]
                [results.add(TransformedData(trs_id, trs, rule)) for trs in transformations]
        
        # Clear blacklist dictionary
        if text_helper.preserve_text: text_helper.remove_from_blacklist(sentences)
        
        df = pd.DataFrame.from_records([s.to_dict() for s in list(results)]).drop_duplicates('sentence')
        
        # Select sample rows according to the max output value
        if self._max_outputs >= 1 :
            original_df = df[df['rule'] == 'original'] 
            aug_df = df[df['rule'] != 'original'] 
            cond_sample = lambda x: x.sample(n = self._max_outputs - 1) if (x.shape[0] >= self._max_outputs - 1) else x
            sampled_df = aug_df.groupby('id').apply(cond_sample)
            df = original_df.append(sampled_df, ignore_index=True)
            
        return df.sort_values('id')
