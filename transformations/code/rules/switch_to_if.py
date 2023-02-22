﻿from __future__ import annotations
from transformations.transformation import Transformation
from transformations.code.utils.code_helper import JT_JAR_PATH, extract_code_specs, tokenize_method

import subprocess

class SwitchToIf(Transformation):
    """
    Code transformation rule from the JavaTransformer tool
    "Replaces a switch statement in a method with an equivalent if statement."
    
    Code reference: https://github.com/mdrafiqulrabin/JavaTransformer/blob/master/src/main/java/SwitchToIf.java
    """
    
    def generate(self, sentence: str):
        sentence, block_line, start_char, end_char = extract_code_specs(sentence, '<START>', '<END>')
        output = subprocess.run(['java', '-jar', JT_JAR_PATH, sentence, 'SwitchToIf',
                                 str(block_line), str(start_char), str(end_char)],
                                stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
        result = output.stdout.decode('utf-8')
        
        transformations = result.split('<<PLACEHOLDER>>') if '<<PLACEHOLDER>>' in result else []
        transformations = [tokenize_method(trn) for trn in transformations if trn.strip() != ''] # clean sentences
        return transformations
