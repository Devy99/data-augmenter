from __future__ import annotations
from abc import ABC, abstractmethod

class Transformation(ABC):
    """
    Abstract Class of the strategy adopted to generate transformed sentences
    """

    def __init__(self, seed=0, verbose=False, max_outputs=-1):
        self.seed = seed
        self.verbose = verbose
        self.max_outputs = max_outputs
        if self.verbose:
            print(f"Loading Operation {self.name()}")

    @abstractmethod
    def generate(self, sentence: str):
        pass
