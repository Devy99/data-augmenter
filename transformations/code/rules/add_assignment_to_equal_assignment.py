from __future__ import annotations
from transformations.transformation import Transformation
from transformations.code.utils.code_helper import SPAT_JAR_PATH, extract_code_specs, preserve_closest_block, reverse_protection

import subprocess

class AddAssignmentToEqualAssignment(Transformation):
    """
    Code transformation rule from the SPAT tool
    "Change the assignment x += 1 into x = x + 1."
    
    Code reference: https://github.com/Santiago-Yu/SPAT/blob/master/src/spat/rules/AddAssignemnt2EqualAssignment.java
    """
    
    def generate(self, sentence: str):
        sentence, block_line, start_char, end_char = extract_code_specs(sentence, '<START>', '<END>')
        output = subprocess.run(['java', '-jar', SPAT_JAR_PATH, sentence, 'AddAssignment2EqualAssignment', str(self.max_outputs),
                                str(block_line), str(preserve_closest_block), str(start_char), str(end_char), str(reverse_protection)],
                                stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
        result = output.stdout.decode('utf-8')
        
        transformations = result.split('<<PLACEHOLDER>>') if '<<PLACEHOLDER>>' in result else []
        return [trn.strip() for trn in transformations if trn.strip() != ''] # clean sentences
