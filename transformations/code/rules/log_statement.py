from __future__ import annotations
from transformations.transformation import Transformation
from transformations.code.utils.code_helper import JT_JAR_PATH, extract_code_specs, preserve_closest_block, reverse_protection

import subprocess

class LogStatement(Transformation):
    """
    Code transformation rule from the JavaTransformer tool
    "Adds System.out.println("log"); at a random location in a block statement."
    
    Code reference: https://github.com/mdrafiqulrabin/JavaTransformer/blob/master/src/main/java/LogStatement.java
    """
    
    def generate(self, sentence: str):
        sentence, block_line, start_char, end_char = extract_code_specs(sentence, '<START>', '<END>')
        output = subprocess.run(['java', '-jar', JT_JAR_PATH, sentence, 'LogStatement',
                                str(block_line), str(preserve_closest_block), str(start_char), str(end_char), str(reverse_protection)],
                                stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
        result = output.stdout.decode('utf-8')
        
        transformations = result.split('<<PLACEHOLDER>>') if '<<PLACEHOLDER>>' in result else []
        return [trn.strip() for trn in transformations if trn.strip() != ''] # clean sentences
