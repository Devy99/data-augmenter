from __future__ import annotations
from pathlib import Path
from transformers import *
from utils.threading_helper import synchronized

import os, sys, pickle, shutil

cached_objs = []
CACHE_FOLDER = os.path.join(sys.path[0], 'cache')

class CachedObj():
    def __init__(self, var, tag) -> None:
        self._var = var
        self._tag = tag

def first(iterable, default=None):
  for ele in iterable:
    return ele
  return default
	

"""
def download_resources():
    # Multilingual back translation
    if get_file('facebook-m2m100_418M-model', store=False) == None:
        model = M2M100ForConditionalGeneration.from_pretrained("facebook/m2m100_418M")
        add_file(model, "facebook-m2m100_418M-model")
        
    if get_file('facebook-m2m100_418M-tokenizer', store=False) == None:    
        tokenizer = M2M100Tokenizer.from_pretrained("facebook/m2m100_418M")
        add_file(tokenizer, "facebook-m2m100_418M-tokenizer")
    
    # Neural question paraphraser
    if get_file('ramsrigouthamg-t5_paraphraser-model', store=False) == None:
        model = T5ForConditionalGeneration.from_pretrained("ramsrigouthamg/t5_paraphraser")
        add_file(model, "ramsrigouthamg-t5_paraphraser-model")
        
    if get_file('ramsrigouthamg-t5_paraphraser-tokenizer', store=False) == None:
        tokenizer = T5Tokenizer.from_pretrained("ramsrigouthamg/t5_paraphraser")
        add_file(tokenizer, "ramsrigouthamg-t5_paraphraser-tokenizer")
    
    # Style paraphraser
    if get_file('filco306-gpt2-base-style-paraphraser-model', store=False) == None:
        model = GPT2LMHeadModel.from_pretrained('filco306/gpt2-base-style-paraphraser')
        add_file(model, 'filco306-gpt2-base-style-paraphraser-model')
        
    if get_file('filco306-gpt2-base-style-paraphraser-tokenizer', store=False) == None:
        tokenizer = GPT2Tokenizer.from_pretrained('filco306/gpt2-base-style-paraphraser')
        add_file(tokenizer, 'filco306-gpt2-base-style-paraphraser-tokenizer')
    
    # Adequacy
    if get_file('prithivida-parrot_adequacy_model-model', store=False) == None:
        model = AutoModelForSequenceClassification.from_pretrained('prithivida/parrot_adequacy_model')
        add_file(model, 'prithivida-parrot_adequacy_model-model')
        
    if get_file('prithivida-parrot_adequacy_model-tokenizer', store=False) == None:
        tokenizer = AutoTokenizer.from_pretrained('prithivida/parrot_adequacy_model')
        add_file(tokenizer, 'prithivida-parrot_adequacy_model-tokenizer')
    
    # Styleformer
    if get_file('prithivida-informal_to_formal_styletransfer-model', store=False) == None:
        model = AutoModelForSeq2SeqLM.from_pretrained('prithivida/informal_to_formal_styletransfer')
        add_file(model, 'prithivida-informal_to_formal_styletransfer-model')
        
    if get_file('prithivida-informal_to_formal_styletransfer-tokenizer', store=False) == None:
        tokenizer = AutoTokenizer.from_pretrained('prithivida/informal_to_formal_styletransfer')
        add_file(tokenizer, 'prithivida-informal_to_formal_styletransfer-tokenizer')
        
    if get_file('prithivida-formal_to_informal_styletransfer-model', store=False) == None:
        model = AutoModelForSeq2SeqLM.from_pretrained('prithivida/formal_to_informal_styletransfer')
        add_file(model, 'prithivida-formal_to_informal_styletransfer-model')
        
    if get_file('prithivida-formal_to_informal_styletransfer-tokenizer', store=False) == None:
        tokenizer = AutoTokenizer.from_pretrained('prithivida/formal_to_informal_styletransfer')
        add_file(tokenizer, 'prithivida-formal_to_informal_styletransfer-tokenizer')

    # Back translation
    if get_file('facebook-wmt19-en-de-model', store=False) == None:
        model = FSMTForConditionalGeneration.from_pretrained('facebook/wmt19-en-de')
        add_file(model, 'facebook-wmt19-en-de-model')
        
    if get_file('facebook-wmt19-en-de-tokenizer', store=False) == None:
        tokenizer = FSMTTokenizer.from_pretrained('facebook/wmt19-en-de')
        add_file(tokenizer, 'facebook-wmt19-en-de-tokenizer')

    if get_file('facebook-wmt19-de-en-model', store=False) == None:
        model = FSMTForConditionalGeneration.from_pretrained('facebook/wmt19-de-en')
        add_file(model, 'facebook-wmt19-de-en-model')
        
    if get_file('facebook-wmt19-de-tokenizer', store=False) == None:
        tokenizer = FSMTTokenizer.from_pretrained('facebook/wmt19-de-en')
        add_file(tokenizer, 'facebook-wmt19-de-tokenizer')

    try:
        spacy.load("en_core_web_sm")
    except Exception as e:
        download(model="en_core_web_sm")
        
    # Download only if the resource does not exist
    try:
        nltk.data.find('corpora/wordnet')
    except LookupError:
        nltk.download("wordnet", quiet=True)
    
    # Load in main memory wordent synsets
    wordnet.ensure_loaded() 
    synsets = {}
    pos_list = ['a', 's', 'v', 'n', 'r']
    for pos in pos_list:
        synsets[pos] = {}
        lemmas = set(chain(*[s.lemma_names() for s in wordnet.all_synsets(pos=pos)]))
        for lemma in lemmas:
            synsets[pos][lemma] = wordnet.synsets(lemma)
            
    cached_objs.append(CachedObj(synsets, 'wordnet_synsets'))
"""

@synchronized
def get_file(tag: str, store: bool = True) -> object:
    """
    Retrieve, if exists, a certain file from the cache. Loads the first two objects requested by the client into memory.

    :param tag: identifier of the file to retrieve
    :param store: if True, save the object in the main memory
    :return: the object saved in the file
    """
    
    # Check whether the object is in the main memory
    obj = first(obj for obj in cached_objs if obj._tag == tag)
    if obj != None: 
        return obj._var
    
    try:
        filepath = os.path.join(CACHE_FOLDER, f'{tag}.cache')
        var = pickle.load(open(filepath, "rb"))
    except (OSError):
        return None
    
    # Update list of cached objects
    if store:
        obj = CachedObj(var, tag)
        #if len(cached_objs) == 2:
        #    cached_objs.clear()
        cached_objs.append(obj)
    
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
