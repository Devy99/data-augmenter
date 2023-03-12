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

def load_reserved_words():
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

def is_protected(word: str, sentence: str):
    if not preserve_text: return False
    return (word in reserved_words) or is_camel_case(word) or is_in_quotes(word, sentence) or from_code_snippet(word, sentence)


def is_camel_case(word: str):
    return word != word.lower() and word != word.upper() and '_' not in word

def find_quotations(sentence: str):
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

def is_in_quotes(word: str, sentence: str):
    # Extract quotations
    quotations = find_quotations(sentence)
    symbols_blacklist = '!"#$%&()*+,-./:;<=>?@[\]^_`{|}~'
    quotations = [q.translate(str.maketrans(' ', ' ', symbols_blacklist)) for q in quotations]
    protected_words = list(itertools.chain(*[ele.split() for ele in quotations]))
    return word in protected_words


#### CODE EXTRACTION ####
def from_code_snippet(word, sentence):
    if sentence not in sentences_blacklist.keys():
        sentences_blacklist[sentence] = extract_java_code(sentence)
    
    snippets = sentences_blacklist[sentence] 
    tokens = set(itertools.chain(*[snippet.split() for snippet in snippets]))
    return word in tokens

def extract_java_code(sentence):
    snippets = []
    
    tokens, size = sentence.split(), 3
    length = len(tokens) - size + 1
    last_index = None
    
    if len(tokens) > 100 or not any(keyword in tokens for keyword in JAVA_KEYWORDS): return []
    
    for i in range(length):
        if last_index != None and i < last_index:
            continue
        else:
            last_index = None
            
        remaining_tokens = tokens[i:]
        if not any(keyword in remaining_tokens for keyword in JAVA_KEYWORDS): break
        
        ti = i + size
        last_snippet = None
        fail_count = 0
        while True:
            t = tokens[i: i + ti]
            string = " ".join(t)
            if is_java(string): 
                last_snippet, last_index = string, ti
            else:
                fail_count += 1
            
            ti += 1
            if ti >= len(tokens) or fail_count == 5: break
        
        if last_snippet != None: 
            snippets.append(last_snippet)
        
    return snippets

def is_java(code):
    code = "class Main { public static void main(String[] args) {" + code + ";} }"
    
    try:     
        tokens = tokenize(code)
        parser = Parser(tokens)
        parser.parse()
    except Exception: 
        return False
    return True