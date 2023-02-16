from __future__ import annotations
from logic.data import Data
from logic.text_data import TextData
from logic.code_data import CodeData

import pandas as pd

class TextCodeData(Data):
    """
    Specialization of the 'Data' class that takes as input both text and code data 
    """
    
    def __init__(self, filepath: str, config: dict, verbose=False):
            self._filepath = filepath
            self._verbose = verbose
        
            self._config = config
            self._max_outputs = config['text-code']['max-outputs']
            self._barrier = None

    def augment(self, chunk: pd.DataFrame) -> pd.DataFrame:
        
        # Assign this barrier to TextData and CodeData instances
        txt_data = TextData(self._filepath, self._config['text'])
        txt_data.barrier = self._barrier
        
        code_data = CodeData(self._filepath, self._config['code'])
        code_data.barrier = self._barrier
        
        # Augment both text and code data
        aug_snt = txt_data.augment(chunk)
        aug_code = code_data.augment(chunk)
        
        # Compute all the possible combinations
        df = pd.merge(aug_snt, aug_code, how='outer', on = 'id')
        
        # Select sample rows according to the max output value
        if self._max_outputs >= 1 :
            original_df = df[(df['rule_x'] == 'original') & (df['rule_y'] == 'original')] 
            aug_df = df[(df['rule_x'] != 'original') | (df['rule_y'] != 'original')] 
            
            cond_sample = lambda x: x.sample(n = self._max_outputs - 1) if (x.shape[0] >= self._max_outputs - 1) else x
            sampled_df = aug_df.groupby('id').apply(cond_sample)
            df = original_df.append(sampled_df, ignore_index=True)
        
        return df.sort_values('id')
