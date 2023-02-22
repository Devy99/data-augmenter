from __future__ import annotations
from transformations.transformation import Transformation
from transformations.code.utils.code_helper import SPAT_JAR_PATH, extract_code_specs, tokenize_method

import subprocess

class LoopIfContinueToElse(Transformation):
    """
    Code transformation rule from the SPAT tool
    "Replace the if-continue statement in a loop block with if-else statement."
    
    Code reference: https://github.com/Santiago-Yu/SPAT/blob/master/src/spat/rules/LoopIfContinue2Else.java
    """
    
    def generate(self, sentence: str):
        sentence, block_line, start_char, end_char = extract_code_specs(sentence, '<START>', '<END>')
        output = subprocess.run(['java', '-jar', SPAT_JAR_PATH, sentence, 'LoopIfContinue2Else', str(self.max_outputs),
                                 str(block_line), str(start_char), str(end_char)],
                                stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
        result = output.stdout.decode('utf-8')
        
        transformations = result.split('<<PLACEHOLDER>>') if '<<PLACEHOLDER>>' in result else []
        transformations = [tokenize_method(trn) for trn in transformations if trn.strip() != ''] # clean sentences
        return transformations
