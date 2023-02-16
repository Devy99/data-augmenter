from __future__ import annotations
from typing import List
from transformations.transformation import Transformation
     
from os import listdir
from os.path import isfile, join
import os, sys, itertools

class Generator():
    """
    Generator class augments a sentence according to a specific transformation rule
    """
    
    RULES_PACKAGE = ''
    RULES_PATH = ''

    def __init__(self) -> None:
        self._rule = None
        self._available_rules = self.__load_rules()

    @property
    def rule(self) -> Transformation:
        return self._rule

    @rule.setter
    def rule(self, rule: Transformation) -> None:
        """
        Define the transformation rule for data augmentation
        """
        self._rule = rule
        
    @property
    def available_rules(self) -> List[Transformation]:
        return self._available_rules

    def run(self, sentence: str) -> List[str]:
        """
        Augment a sentence with the transformation rule defined by the generator
        :param sentence: sentence to augment
        :return: list of transformed sentences
        """
        
        if self._rule:
            results = self._rule.generate(sentence)
            max_outputs = self._rule.max_outputs
            results = [res for res in itertools.islice(results, max_outputs)] if max_outputs != -1 else results
            return results
        
    
    def rule_exists(self, name: str) -> bool:
        """
        Check if the given rule name is available
        :param name: name of the rule to check
        :return: True/False
        """
        return name in self._available_rules

    def __load_rules(self) -> List[str]:
        """
        Search all the available rule in the rules folder
        :return: list of strings representing the existing rules
        """
        
        scanners_path = os.path.join(sys.path[0], self.RULES_PATH)
        return [f.split('.')[0] for f in listdir(scanners_path) if isfile(join(scanners_path, f))]
