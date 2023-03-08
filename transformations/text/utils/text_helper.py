import re, itertools

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

# Tool args
preserve_text = False

def is_camel_case(word: str):
    return word != word.lower() and word != word.upper() and '_' not in word

def is_in_quotes(word: str, sentence: str):
    # Normalize quotes
    types = ["'", "‘", "’", "´", "“", "”", "--"]
    normalized = sentence
    for type in types:
        normalized = normalized.replace(type, "\"")
    
    # Extract quotations
    quotations = re.findall('"([^"]*)"', normalized)
    protected_words = list(itertools.chain(*[ele.split() for ele in quotations]))
    return word in protected_words


def is_protected(word: str, sentence: str):
    if not preserve_text: return False
    return (word in JAVA_KEYWORDS) or (word in JAVA_IDENTIFIERS) or \
           (word in JAVA_LITERAL_VALUES) or is_camel_case(word) or is_in_quotes(word, sentence)
