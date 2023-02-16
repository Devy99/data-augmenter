from __future__ import annotations
from transformations.transformation import Transformation
from transformers import FSMTForConditionalGeneration, FSMTTokenizer
from utils import cache_helper

class BackTranslation(Transformation):
    heavy = True
    keywords = ["lexical", "model-based", "syntactic", "high-coverage"]

    def __init__(self, seed=0, max_outputs=1, num_beams=2):
        super().__init__(seed, max_outputs=max_outputs)
        if self.verbose:
            print("Starting to load English to German Translation Model.\n")
        name_en_de = "facebook/wmt19-en-de"
        
        cache_file = name_en_de.replace('/', '-')
        model_en_de = cache_helper.get_file(f"{cache_file}-model")
        if model_en_de is None:
            model_en_de = FSMTForConditionalGeneration.from_pretrained(name_en_de)
            cache_helper.add_file(model_en_de, f"{cache_file}-model")
                
        tokenizer_en_de = cache_helper.get_file(f"{cache_file}-tokenizer")
        if tokenizer_en_de is None:
            tokenizer_en_de = FSMTTokenizer.from_pretrained(name_en_de)
            cache_helper.add_file(tokenizer_en_de, f"{cache_file}-tokenizer")
        
        self.tokenizer_en_de = tokenizer_en_de
        self.model_en_de = model_en_de
        
        if self.verbose:
            print("Completed loading English to German Translation Model.\n")
            print("Starting to load German to English Translation Model:")
        name_de_en = "facebook/wmt19-de-en"
        
        cache_file = name_de_en.replace('/', '-')
        model_de_en = cache_helper.get_file(f"{cache_file}-model")
        if model_de_en is None:
            model_de_en = FSMTForConditionalGeneration.from_pretrained(name_de_en)
            cache_helper.add_file(model_de_en, f"{cache_file}-model")
                
        tokenizer_de_en = cache_helper.get_file(f"{cache_file}-tokenizer")
        if tokenizer_de_en is None:
            tokenizer_de_en = FSMTTokenizer.from_pretrained(name_de_en)
            cache_helper.add_file(tokenizer_de_en, f"{cache_file}-tokenizer")
        
        self.tokenizer_de_en = tokenizer_de_en
        self.model_de_en = model_de_en
        
        self.num_beams = num_beams
        if self.verbose:
            print("Completed loading German to English Translation Model.\n")

    def back_translate(self, en: str):
        try:
            de = self.en2de(en)
            en_new = self.de2en(de)
        except Exception:
            #print("Returning Default due to Run Time Exception")
            en_new = en
        return en_new

    def en2de(self, input):
        input_ids = self.tokenizer_en_de.encode(input, return_tensors="pt")
        outputs = self.model_en_de.generate(input_ids)
        decoded = self.tokenizer_en_de.decode(
            outputs[0], skip_special_tokens=True
        )
        if self.verbose:
            print(decoded)  # Maschinelles Lernen ist groÃŸartig, oder?
        return decoded

    def de2en(self, input):
        input_ids = self.tokenizer_de_en.encode(input, return_tensors="pt")
        outputs = self.model_de_en.generate(
            input_ids,
            num_return_sequences=self.max_outputs,
            num_beams=self.num_beams,
        )
        predicted_outputs = []
        for output in outputs:
            decoded = self.tokenizer_de_en.decode(
                output, skip_special_tokens=True
            )
            # TODO: this should be able to return multiple sequences
            predicted_outputs.append(decoded)
        if self.verbose:
            print(predicted_outputs)  # Machine learning is great, isn't it?
        return predicted_outputs

    def generate(self, sentence: str):
        perturbs = self.back_translate(sentence)
        return perturbs
