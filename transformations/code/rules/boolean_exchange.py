from __future__ import annotations
from transformations.transformation import Transformation
from transformations.code.utils.code_helper import JAR_PATH, extract_code_specs, tokenize_method

import subprocess

class BooleanExchange(Transformation):
    """
    Code transformation rule from the JavaTransformer tool
    "Switches the value of a boolean variable in a method from true to false or vice versa, and propagates this change in 
    the method to ensure a semantic equivalence of the transformed method with the original method."
    
    Code reference: https://github.com/mdrafiqulrabin/JavaTransformer/blob/master/src/main/java/BooleanExchange.java
    """
    
    def generate(self, sentence: str):
        sentence, block_line, start_char, end_char = extract_code_specs(sentence, '<START>', '<END>')
        output = subprocess.run(['java', '-jar', JAR_PATH, sentence, 'BooleanExchange',
                                 str(block_line), str(start_char), str(end_char)], stdout=subprocess.PIPE)
        result = output.stdout.decode('utf-8')
        
        transformations = result.split('<<PLACEHOLDER>>')
        transformations = [tokenize_method(trn) for trn in transformations if trn.strip() != ''] # clean sentences
        return transformations
