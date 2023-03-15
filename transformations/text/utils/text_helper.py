from typing import List, Set
from javalang.tokenizer import tokenize
from javalang.parser import Parser
import os, re, itertools

JAVA_KEYWORDS = [
    '_', 'abstract', 'assert', 'boolean', 'break', 'byte', 'case', 'catch', 'char', 'class',
    'const', 'continue', 'default', 'do', 'double', 'else', 'enum', 'extends', 'final', 'finally',
    'float', 'for', 'goto', 'if', 'implements', 'import', 'instanceof', 'int', 'interface', 'long',
    'native', 'new', 'package', 'private', 'protected', 'public', 'return', 'short', 'static', 'strictfp', 
    'super', 'switch', 'synchronized', 'this', 'throw', 'throws', 'transient', 'try', 'void', 'volatile', 'while',
    ]

JAVA_IDENTIFIERS = [
        'exports', 'module', 'non-sealed', 'open', 'opens', 'permits', 'provides', 'record',
        'requires', 'sealed', 'to', 'transitive', 'uses', 'var', 'with', 'yield'
    ]

JAVA_LITERAL_VALUES = [
        'true', 'false', 'null'
    ]

def load_reserved_words() -> Set:
    words = []
    
    # Add Java keywords
    words.extend(JAVA_KEYWORDS)
    words.extend(JAVA_IDENTIFIERS)
    words.extend(JAVA_LITERAL_VALUES)
    
    # Add programming common terms from se-thesaurus
    thesaurus_path = os.path.join('transformations','text','utils','reserved_words', 'se-thesaurus.txt')
    with open(thesaurus_path, 'r') as file:
        for line in file:
            tokens = line.strip().split(',')
            tokens = [t.replace('_',' ') for t in tokens]
            words.extend(tokens)
    
    return set(words)

reserved_words = load_reserved_words()
sentences_blacklist = {}

# Tool args
preserve_text = False

def is_protected(word: str, sentence: str) -> bool:
    if not preserve_text: return False
    return (word in reserved_words) or is_camel_case(word) or is_in_quotes(word, sentence) or from_code_snippet(word, sentence)


def is_camel_case(word: str) -> bool:
    return word != word.lower() and word != word.upper() and '_' not in word

#### QUOTE EXTRACTION ####
def find_quotations(sentence: str) -> List[str]:
    # Normalize quotes
    normalized = sentence.strip()
    types = ["''", "‘", "’", "´", "“", "”", "--"]
    for type in types:
        normalized = normalized.replace(type, "\"")
    
    # Handle the apostrophe
    normalized = re.sub("(?<!\w)'|'(?!\w)", "\"", normalized)
    if normalized.startswith("'"): normalized.replace("'", "\"", 1)
    if normalized.endswith("'"): normalized = normalized[:-1] + "\""
        
    # Extract quotations
    return re.findall('"([^"]*)"', normalized)

def is_in_quotes(word: str, sentence: str) -> bool:
    # Extract quotations
    quotations = find_quotations(sentence)
    symbols_blacklist = '!"#$%&()*+,-./:;<=>?@[\]^_`{|}~'
    quotations = [q.translate(str.maketrans(' ', ' ', symbols_blacklist)) for q in quotations]
    protected_words = list(itertools.chain(*[ele.split() for ele in quotations]))
    return word in protected_words


#### CODE EXTRACTION ####
def from_code_snippet(word: str, sentence: str) -> bool:
    if sentence not in sentences_blacklist.keys():
        sentences_blacklist[sentence] = extract_java_code(sentence)
    
    snippets = sentences_blacklist[sentence] 
    tokens = set(itertools.chain(*[tokenize_snippet(code) for code in snippets]))
    return word in tokens

def tokenize_snippet(code: str) -> List[str]:
    try:     
        return [token.value for token in tokenize(code)]
    except Exception: 
        return [token for token in code.split()]
    

def remove_from_blacklist(sentences: List[str]) -> None:
    for key in sentences:
        sentences_blacklist.pop(key, None)

def extract_java_code(sentence: str) -> List[str]:
    # Define the length of the initial expression
    tokens, size = sentence.split(), 3
    last_index = None
    
    # Check if there is any java keyword in the string
    if not contains_java_code(tokens): return []
    
    snippets = []
    length = len(tokens) - size + 1
    for x in range(length):
        # Consume tokens already seen
        if last_index != None and x < last_index:
            continue
        
        # Check if there is any java keyword in the remaining tokens
        remaining_tokens = tokens[x:]
        if not contains_java_code(remaining_tokens): break
        
        y = x + size
        last_snippet, last_index, fail_count = None, None, 0
        while True:
            t = tokens[x:y]
            string = " ".join(t)
            if is_java(string): 
                last_snippet, last_index = string, y
            else: # Count number of non-java consecutive expression
                fail_count += 1
            
            if y >= len(tokens) or fail_count == 25: 
                break
            y = y + 1
        
        if last_snippet != None: 
            snippets.append(last_snippet)
        
    return snippets

def is_java(code: str) -> bool:
    code = "class Main { public static void main(String[] args) {" + code + ";} }"
    
    try:     
        tokens = tokenize(code)
        parser = Parser(tokens)
        parser.parse()
    except Exception: 
        return False
    return True

def contains_java_code(tokens: List[str]) -> bool:
    keywords = []
    keywords.extend(JAVA_KEYWORDS)
    keywords.extend(JAVA_IDENTIFIERS)
    keywords.extend(JAVA_LITERAL_VALUES)
    
    return any(keyword in tokens for keyword in keywords) or any(is_camel_case(token) for token in tokens)