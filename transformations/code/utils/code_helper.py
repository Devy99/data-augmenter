
from javalang.tokenizer import tokenize
import os, sys

JAR_PATH = os.path.join(sys.path[0], 'transformations', 'code', 'utils', 'JavaTransformer.jar')


def tokenize_method(method):
  return ' '.join(token.value for token in tokenize(method))

def extract_code_specs(code: str, start_tag: str, end_tag: str):
    sentence = code
    block_line = False
    start_char, end_char = 0, 0
    
    if start_tag in sentence and end_tag in sentence:
        block_line = True
            
        parts = sentence.split(start_tag)
        left_split, right_split = parts[0], parts[1]
        start_char = len(left_split)
        sentence = left_split
            
        parts = right_split.split(end_tag)
        left_split, right_split = parts[0], parts[1]
        sentence += left_split
        end_char = len(sentence)
            
        sentence += right_split
        
    return sentence, block_line, start_char, end_char
