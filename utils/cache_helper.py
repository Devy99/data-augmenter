﻿from __future__ import annotations
from pathlib import Path

import os, sys, pickle, shutil, threading

cachedObjs = []
CACHE_FOLDER = os.path.join(sys.path[0], 'cache')

class CachedObj():
    def __init__(self, var, tag) -> None:
        self._var = var
        self._tag = tag

def first(iterable, default=None):
  for ele in iterable:
    return ele
  return default
	
def synchronized(func):
    func.__lock__ = threading.Lock()
    def synced_func(*args, **kws):
        with func.__lock__:
            return func(*args, **kws)

    return synced_func

@synchronized
def get_file(tag: str) -> object:
    """
    Retrieve, if exists, a certain file from the cache. Loads the first two objects requested by the client into memory.

    :param tag: identifier of the file to retrieve
    :return: the object saved in the file
    """
    
    # Check whether the object is in the main memory
    obj = first(obj for obj in cachedObjs if obj._tag == tag)
    if obj != None: 
        return obj._var
    
    try:
        filepath = os.path.join(CACHE_FOLDER, f'{tag}.cache')
        var = pickle.load(open(filepath, "rb"))
    except (OSError):
        return None
    
    # Update list of cached objects
    obj = CachedObj(var, tag)
    if len(cachedObjs) == 2:
        cachedObjs.clear()
    cachedObjs.append(obj)
    
    return var
    

def add_file(var: object, tag: str) -> bool:
    """
    Add a new file in the cache and label it with a specific identifier

    :param var: object to save
    :param tag: identifier of the file to save
    :return: True if the operation is successful, False otherwise
    """

    if not os.path.exists(CACHE_FOLDER):
        init_cache_folder()
    
    filepath = os.path.join(CACHE_FOLDER, f'{tag}.cache')
    
    try:
        pickle.dump(var, open(filepath, "wb"))
    except (OSError):
        return False
    
    return True

def init_cache_folder():    
    """
    Create the cache folder if it does not exist
    """
    dirpath = Path(CACHE_FOLDER)
    if not dirpath.exists():
        os.mkdir(dirpath)

def clear_cache() -> None:
    """
    Remove all files from the cache directory
    """
    dirpath = Path(CACHE_FOLDER)
    if dirpath.exists() and dirpath.is_dir():
        shutil.rmtree(dirpath)
