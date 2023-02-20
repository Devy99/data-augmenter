from __future__ import annotations
from abc import ABC, abstractmethod
from multiprocessing.pool import ThreadPool
from pandas.io.parsers import TextFileReader
from threading import Barrier

import csv, threading
import pandas as pd

class Data(ABC):
    """
    Class representing the data taken as input by the tool. 
    """

    def __init__(self, filepath: str, config: dict, verbose=False):
        self._filepath = filepath
        self._verbose = verbose
        
        self._data_column = config['data-column']
        self._active_rules = config['active-rules']
        self._max_outputs = config['max-outputs']
        self._outputs_per_rule = config['outputs-per-rule']
        
        self._barrier = None
        
    
    @property
    def barrier(self) -> Barrier:
        return self._barrier

    @barrier.setter
    def barrier(self, barrier: Barrier) -> None:
        """
        Setter of the barrier to be used in order to synchronize threads during the computation.
        """
        self._barrier = barrier
        
    def compute(self, out_fp: str = 'output.tsv', workers: int = 1, chunk_size: int = 100) -> None:
        """
        Main function apt to perform the augmentation operation on the entire dataset taken as input
        and export it to an output file. It reads the dataset in chunks and assigns them to a specific number of threads.
        :param out_fp: filepath in which the augmented dataset will be saved
        :param workers: number of threads to which to assign chunks of the dataset
        :param chunk_size: size of dataset chunk to be read and augmented by each thread
        """
        reader = self.__load_reader(self._filepath, chunk_size)
        
        # Distribute the chunks among threads and add the results to the output file
        self._barrier = threading.Barrier(workers)
        with ThreadPool(workers) as pool:
            for id, result in enumerate(pool.imap(self.augment, reader)):
                self.__export(result, out_fp)
                if self._verbose: print(f'Total elaborated chunks: {(id + 1) * chunk_size}')
    
    @abstractmethod
    def augment(self, chunk: pd.DataFrame) -> pd.DataFrame:
        """
        Augments a chunk according to the type of the dataset taken as input.
        :param chunk: chunk of the dataset to be augmented
        :return: the augmented chunk of the dataset
        """
        pass
    
    def __export(self, data: pd.DataFrame, out_fp: str) -> None:
        """
        Export a dataset as a CSV file in append mode.
        :param data: dataset to be exported
        :param out_fp: filepath in which to append the dataset 
        """
        data.to_csv(out_fp, sep=',', mode='a', header=False, index=False, quoting=csv.QUOTE_ALL, escapechar='\\')
    
    def __load_reader(self, filepath: str, chunk_size: int) -> TextFileReader:
        """
        Get the reader of the dataset divided into chunks
        :param filepath: filepath of the dataset to be read
        :param chunk_size: size of the portion of the dataset to be read at each iteration
        :return: the dataset reader
        """
        
        chunk_size = 1 if chunk_size <= 0 else chunk_size
        return pd.read_csv(filepath, sep=',', header=None, chunksize=chunk_size)
    