import os, sys, string

JT_JAR_PATH = os.path.join(sys.path[0], 'transformations', 'code', 'utils', 'JavaTransformer.jar')
SPAT_JAR_PATH = os.path.join(sys.path[0], 'transformations', 'code', 'utils', 'SPAT.jar')

def tokenize_method(method):
  clean_str = method.translate({ord(c): ' ' for c in string.whitespace})
  return ' '.join(clean_str.split())

def extract_code_specs(code: str, start_tag: str, end_tag: str):
    sentence = code
    block_line = False
    start_char, end_char = 0, 0
    
    if start_tag in sentence and end_tag in sentence:
      
      if sentence.find(end_tag) < sentence.find(start_tag):
        sentence = sentence.replace(start_tag, ' ').replace(end_tag, ' ')
      else:
        block_line = True
            
        parts = sentence.split(start_tag)
        left_split, right_split = parts[0], parts[1]
        start_char = len(left_split)
        sentence = left_split
            
        parts = right_split.split(end_tag)
        left_split, right_split = parts[0], parts[1]
        sentence += ' ' + left_split
        end_char = len(sentence) + 1
            
        sentence += ' ' + right_split
      
    return sentence, block_line, start_char, end_char
