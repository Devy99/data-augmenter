import os, re, itertools

def load_reserved_words():
    words = []
    
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
    
    # Add Java keywords
    words.extend(JAVA_KEYWORDS)
    words.extend(JAVA_IDENTIFIERS)
    words.extend(JAVA_LITERAL_VALUES)
    
    # Add programming common terms from se-thesaurus
    thesaurus_path = os.path.join('transformations','text','utils','reserved_words', 'se-thesaurus.txt')
    with open(thesaurus_path, 'r') as file:
        for line in file:
            tokens = line.split(',')
            words.extend(tokens)
    
    return words

reserved_words = load_reserved_words()

# Tool args
preserve_text = False

def is_camel_case(word: str):
    return word != word.lower() and word != word.upper() and '_' not in word

def find_quotations(sentence: str):
    # Normalize quotes
    normalized = sentence.strip()
    types = ["''", "‘", "’", "´", "“", "”", "--"]
    for type in types:
        normalized = normalized.replace(type, "\"")
    
    # Handle the apostrophe
    normalized = re.sub("'(?!\w)|(?!\w)'", "\"", normalized)
    normalized = normalized.replace("'", "\"")
    if normalized.startswith("'"): normalized.replace("'", "\"", 1)
    if normalized.endswith("'"): normalized = normalized[:-1] + "\""
        
    # Extract quotations
    return re.findall('"([^"]*)"', normalized)

def is_in_quotes(word: str, sentence: str):
    # Extract quotations
    quotations = find_quotations(sentence)
    protected_words = list(itertools.chain(*[ele.split() for ele in quotations]))
    return word in protected_words


def is_protected(word: str, sentence: str):
    if not preserve_text: return False
    return (word in reserved_words) or is_camel_case(word) or is_in_quotes(word, sentence)

