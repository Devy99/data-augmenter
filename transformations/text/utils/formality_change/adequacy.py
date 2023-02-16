﻿from transformers import AutoModelForSequenceClassification, AutoTokenizer
from utils import cache_helper

class Adequacy():
  
  def __init__(self, model_tag='prithivida/parrot_adequacy_model'):
    
    cache_file = model_tag.replace('/', '-')
    model = cache_helper.get_file(f"{cache_file}-model")
    if model is None:
      model = AutoModelForSequenceClassification.from_pretrained(model_tag)
      cache_helper.add_file(model, f"{cache_file}-model")
            
    tokenizer = cache_helper.get_file(f"{cache_file}-tokenizer")
    if tokenizer is None:
      tokenizer = AutoTokenizer.from_pretrained(model_tag)
      cache_helper.add_file(tokenizer, f"{cache_file}-tokenizer")
    
    self.adequacy_model = model
    self.tokenizer = tokenizer

  def filter(self, input_phrase, para_phrases, adequacy_threshold, device="cpu"):
      top_adequacy_phrases = []
      for para_phrase in para_phrases:
        x = self.tokenizer(input_phrase, para_phrase, return_tensors='pt', max_length=128, truncation=True)
        self.adequacy_model = self.adequacy_model.to(device)
        logits = self.adequacy_model(**x).logits
        probs = logits.softmax(dim=1)
        prob_label_is_true = probs[:,1]
        adequacy_score = prob_label_is_true.item()
        if adequacy_score >= adequacy_threshold:
            top_adequacy_phrases.append(para_phrase)
      return top_adequacy_phrases


  def score(self, input_phrase, para_phrases, adequacy_threshold, device="cpu"):
      adequacy_scores = {}
      for para_phrase in para_phrases:
        x = self.tokenizer(input_phrase, para_phrase, return_tensors='pt', max_length=128, truncation=True)
        x = x.to(device)
        self.adequacy_model = self.adequacy_model.to(device)
        logits = self.adequacy_model(**x).logits
        probs = logits.softmax(dim=1)
        prob_label_is_true = probs[:,1]
        adequacy_score = prob_label_is_true.item()
        if adequacy_score >= adequacy_threshold:
          adequacy_scores[para_phrase] = adequacy_score
      return adequacy_scores
