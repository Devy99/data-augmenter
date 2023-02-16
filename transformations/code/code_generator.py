from __future__ import annotations
from transformations.generator import Generator

import os

class CodeGenerator(Generator):
    
    RULES_PACKAGE = 'transformations.code.rules.'
    RULES_PATH = os.path.join('transformations','code','rules')
    
