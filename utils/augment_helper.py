from __future__ import annotations
from pyclbr import Class

class TransformedData:
    """
    Wrapper class that contains the augmented data information
    
    Attributes:
        id  id of the original statement
        sentence  transformed sentence
        rule  rule applied for the transformation
    """
    def __init__(self, id, sentence, rule):
        self._id = id
        self._sentence = sentence
        self._rule = rule
        
    def to_dict(self):
        return {
            'id': self._id,
            'sentence': self._sentence,
            'rule': self._rule,
        }
    
    def __eq__(self, other): 
        return self._id == other._id and self._sentence == other._sentence and self._rule == other._rule
    
    def __hash__(self):
        return hash((self._id, self._sentence, self._rule))


def get_class( kls: str ) -> Class:
    """
    Retrieve the instance of a specific class
    :param kls: class filepath
    :return: a Class object
    """
    parts = kls.split('.')
    module = ".".join(parts[:-1])
    m = __import__( module )
    for comp in parts[1:]:
        m = getattr(m, comp)            
    return m

