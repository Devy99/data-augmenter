from __future__ import annotations
from transformations.transformation import Transformation
from transformations.code.utils.code_helper import SPAT_JAR_PATH, extract_code_specs, tokenize_method

import subprocess

class ReverseIfElse(Transformation):
    """
    Code transformation rule from the SPAT tool
    "Switch the two code blocks in the if statement and the corresponding else statement"
    
    Code reference: https://github.com/Santiago-Yu/SPAT/blob/master/src/spat/rules/ReveseIf_Else.java
    """
    
    def generate(self, sentence: str):
        sentence, block_line, start_char, end_char = extract_code_specs(sentence, '<START>', '<END>')
        output = subprocess.run(['java', '-jar', SPAT_JAR_PATH, sentence, 'ReverseIfElse', str(self.max_outputs),
                                 str(block_line), str(start_char), str(end_char)], stdout=subprocess.PIPE)
        result = output.stdout.decode('utf-8')
        
        transformations = result.split('<<PLACEHOLDER>>')
        transformations = [tokenize_method(trn) for trn in transformations if trn.strip() != ''] # clean sentences
        return transformations
