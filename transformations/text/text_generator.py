from __future__ import annotations
from transformations.generator import Generator

import os


class TextGenerator(Generator):
    
    RULES_PACKAGE = 'transformations.text.rules.'
    RULES_PATH = os.path.join('transformations','text','rules')
    
