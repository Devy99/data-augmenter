from __future__ import annotations
from transformations.transformation import Transformation
from transformers import GPT2LMHeadModel, GPT2Tokenizer
from transformers.utils import logging
from utils import cache_helper

import re
import nltk
import numpy as np
import torch

from transformations.text.utils.style_paraphraser.style_paraphraser import (
    Instance,
    _beam_search,
    _sample_sequence,
)


"""
    Note: This codebase is based upon, adapted and refactored from code
    from this repository:
    https://github.com/martiansideofthemoon/style-transfer-paraphrase
"""

MODELS_SUPPORTED = {
    "Bible": "filco306/gpt2-bible-paraphraser",
    "Basic": "filco306/gpt2-base-style-paraphraser",
    "Shakespeare": "filco306/gpt2-shakespeare-paraphraser",
    "Tweets": "filco306/gpt2-tweet-paraphraser",
    "Switchboard": "filco306/gpt2-switchboard-paraphraser",
    "Romantic poetry": "filco306/gpt2-romantic-poetry-paraphraser",
}

MAX_PARAPHRASE_LENGTH = 100

BASE_CONFIG = {
    "max_total_length": MAX_PARAPHRASE_LENGTH,
    "max_prefix_length": int(MAX_PARAPHRASE_LENGTH / 2),
    "max_suffix_length": int(MAX_PARAPHRASE_LENGTH / 2),
}


class StyleParaphraser(Transformation):

    """
        Sentence transformation rule from the NL-Augmenter library
        "Style transfer paraphraser, using a GPT2-model of choice."
        Args:
            style : str
                The style to use. Options include Bible, Shakespeare, Basic, Romantic Poetry, Switchboard and Tweets.
            device : device to use for computations.
                Default: None, and it will then resort to CUDA if available, else CPU.
            upper_length :
                The maximum length.
                Options: "eos" or "same_N" (e.g., "same_5"), where N will be the max_length.
                    "eos" means the maximum length is the length of the sentence a paraphrase is generated for.
                    "same_N" means the the length of the original sentence + N.
            beam_size : size of the beam during beam search (if top_p == 0.0)
                Default: 1
            top_p : float
                top_p sampling, between 0.0 and 1.0
                Default: 0.0 (meaning using a greedy approach)
            temperate : float
                Sampling temperate
                Default: 0.0
        
        Code reference: https://github.com/GEM-benchmark/NL-Augmenter/tree/main/nlaugmenter/transformations/style_paraphraser
    """

    def __init__(
        self,
        max_outputs: int = -1,
        style: str = "Basic",
        device=None,
        upper_length="same_5",
        beam_size: int = 1,
        top_p: int = 0.0,
        temperature: float = 0.0,
    ):
        if max_outputs == -1: max_outputs = 10
        super().__init__(max_outputs=max_outputs)
        logging.set_verbosity(40)
        try:
            nltk.data.find("tokenizers/punkt")
        except LookupError:
            nltk.download("punkt")
        self.style = style

        assert (
            style in MODELS_SUPPORTED.keys()
        ), f"Style not supported. The following styles are supported: {', '.join(list(MODELS_SUPPORTED.keys()))}"
        model_path = MODELS_SUPPORTED[style]
        self.args = {}
        self.device = device
        if self.device is None:
            self.device = torch.device(
                "cuda" if torch.cuda.is_available() else "cpu"
            )
        self.args["upper_length"] = upper_length
        self.args["stop_token"] = "eos" if upper_length == "eos" else None
        self.args["beam_size"] = beam_size
        self.args["temperature"] = temperature
        self.args["top_p"] = top_p
        self.args["top_k"] = 1
        self.args["device"] = self.device
        self.config = BASE_CONFIG

        self.config["global_dense_length"] = 0
        
        cache_path = model_path.replace('/','-')
        model = cache_helper.get_file(f"{cache_path}-model")
        if model is None:
            model = GPT2LMHeadModel.from_pretrained(model_path)
            cache_helper.add_file(model, f"{cache_path}-model")
        
        model.to(self.device)
        self.gpt2_model = model  # GPT2ParentModule(gpt2=model, device=device)
            
        tokenizer = cache_helper.get_file(f"{cache_path}-tokenizer", store=False)
        if tokenizer is None:
            tokenizer = GPT2Tokenizer.from_pretrained(model_path)
            cache_helper.add_file(tokenizer, f"{cache_path}-tokenizer")
        self.tokenizer = tokenizer

    def modify_p(self, top_p):
        """Set top_p to another value"""
        self.args["top_p"] = top_p

    def generate(self, sentence, top_p=None, max_outputs: int = 1):
        """
        Generate paraphrases for a batch of outputs - or for the same but with a top_p != 0.0
        sentence : str
            Sentence to paraphrase.
        top_p : float
            top_p sampling, between 0.0 and 1.0
            Default None, resorting to the model's top_p value
        max_outputs : int
            Number of samples to generate for a sentence.
            Note: These will be the exact same if you use a greedy sampling (top_p=0.0), so if max_outputs > 2, makes sure top_p != 0.0.
        """
        sent_text = nltk.sent_tokenize(sentence)

        contexts = [sent_text] * max_outputs

        to_ret = []
        for context_ in contexts:
            instances = []
            for context in context_:
                context_ids = self.tokenizer.convert_tokens_to_ids(
                    self.tokenizer.tokenize(context)
                )

                instance = Instance(
                    self.args,
                    self.config,
                    {"sent1_tokens": context_ids, "sent2_tokens": context_ids},
                )
                instance.preprocess(self.tokenizer)
                global_dense_vectors = np.zeros((1, 768), dtype=np.float32)
                instance.gdv = global_dense_vectors
                instances.append(instance)

            gpt2_sentences = torch.tensor(
                [inst.sentence for inst in instances]
            ).to(self.device)
            segments = torch.tensor([inst.segment for inst in instances]).to(
                self.device
            )
            init_context_size = instances[0].init_context_size
            eos_token_id = self.tokenizer.eos_token_id

            generation_length = (
                None
                if self.args["stop_token"] == "eos"
                else len(gpt2_sentences[0]) - init_context_size
            )

            if self.args["beam_size"] > 1:
                output = _beam_search(
                    model=self.gpt2_model,
                    length=generation_length,
                    context=gpt2_sentences[:, 0:init_context_size],
                    segments=segments[:, 0:init_context_size],
                    eos_token_id=eos_token_id,
                    beam_size=self.args["beam_size"],
                    beam_search_scoring=self.args["beam_search_scoring"],
                )
            else:
                output = _sample_sequence(
                    model=self.gpt2_model,
                    context=gpt2_sentences[:, 0:init_context_size],
                    segments=segments[:, 0:init_context_size],
                    eos_token_id=eos_token_id,
                    length=generation_length,
                    temperature=self.args["temperature"],
                    top_k=self.args["top_k"],
                    top_p=top_p or self.args["top_p"],
                )

            all_output = []
            for out_num in range(len(output)):
                instance = instances[out_num]
                curr_out = output[
                    out_num, instance.init_context_size :  # noqa: E203
                ].tolist()

                if self.tokenizer.eos_token_id in curr_out:
                    curr_out = curr_out[
                        : curr_out.index(self.tokenizer.eos_token_id)
                    ]

                if self.args["upper_length"].startswith("same"):
                    extra = int(self.args["upper_length"].split("_")[-1])
                    curr_out = curr_out[: len(instance.sent1_tokens) + extra]

                all_output.append(
                    self.tokenizer.decode(
                        curr_out,
                        clean_up_tokenization_spaces=True,
                        skip_special_tokens=True,
                    )
                )
            to_ret.append(re.sub("!?\\??\\.+", ".", ". ".join(all_output)))
        return to_ret[:max_outputs]
