from __future__ import annotations
from logic.data import Data
from utils.augment_helper import TransformedData, get_class
from transformations.code.code_generator import CodeGenerator
from transformations.code.utils.code_helper import extract_code_specs
from transformations.code.utils import code_helper

import pandas as pd

class CodeData(Data):
    """
    Specialization of the 'Data' class that takes as input data containing only code 
    """
    
    def __init__(self, filepath: str, config: dict, verbose=False):
        super().__init__(filepath, config, verbose)
        code_helper.preserve_closest_block = config['preserve-closest-block']

    def augment(self, chunk: pd.DataFrame) -> pd.DataFrame:
        results = set()
        
        # Retrieve data from the dataframe chunk 
        code_col = chunk[chunk.columns[self._data_column]]
        code_list = code_col.values.tolist()
        
        # Retrieve available generator rules
        generator = CodeGenerator()
        self._active_rules = list(set(self._active_rules) & set(generator.available_rules))
        
        for sid, code in enumerate(code_list):
            trs_id = chunk.index.values[sid]
            norm_sentence, block_line, start_char, end_char = extract_code_specs(code, '<START>', '<END>') # remove tags to code entities
            results.add(TransformedData(trs_id, norm_sentence, 'original'))
            
            # Apply transformation
            for rule in self._active_rules:
                cname = ''.join([ele.capitalize() for ele in rule.split('_')])
                generator.rule = get_class(generator.RULES_PACKAGE + rule + '.' + cname)(max_outputs=self._outputs_per_rule)
                transformations = generator.run(code)
                
                transformations = [item for item in transformations if item != code]
                [results.add(TransformedData(trs_id, trs, rule)) for trs in transformations]
        
        df = pd.DataFrame.from_records([s.to_dict() for s in results]).drop_duplicates('sentence')
        
        # Select sample rows according to the max output value
        if self._max_outputs >= 1 :
            original_df = df[df['rule'] == 'original'] 
            aug_df = df[df['rule'] != 'original'] 
            cond_sample = lambda x: x.sample(n = self._max_outputs - 1) if (x.shape[0] >= self._max_outputs - 1) else x
            sampled_df = aug_df.groupby('id').apply(cond_sample)
            df = original_df.append(sampled_df, ignore_index=True)
            
        return df.sort_values('id')
