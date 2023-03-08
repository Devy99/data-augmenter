from transformations.transformation import Transformation

import os, json, transformations.text.utils.text_helper as text_helper

def britishize_americanize(string, final_dict):
    """
    Parameters:
        string(str): original string
        final_dict(dict): dictionary with all the different possible words in american and british english
    Returns:
        str: String after replacing the words
    """
    tokens = []
    for word in string.split():
        t = final_dict.get(word, word) if not text_helper.is_protected(word, string) else word
        tokens.append(t)
    # string = " ".join([final_dict.get(word, word) for word in string.split()])
    return " ".join(tokens)

class AmericanizeBritishizeEnglish(Transformation):
    """
    Sentence transformation rule from the NL-Augmenter library
    "This transformation takes a sentence and converts it from british english to american english and vice-versa"
    
    Code reference: https://github.com/GEM-benchmark/NL-Augmenter/tree/main/nlaugmenter/transformations/americanize_britishize_english
    """
    def __init__(self, seed=0, max_outputs=-1):
        super().__init__(seed, max_outputs=max_outputs)

        # Creating a custom vocab dictionary consisting of totally different words for same context
        difference_british_to_american = {
            "trousers": "pants",
            "flat": "apartment",
            "bonnet": "hood",
            "boot": "trunk",
            "lorry": "truck",
            "university": "college",
            "holiday": "vacation",
            "jumper": "sweater",
            "trainers": "sneakers",
            "postbox": "mailbox",
            "biscuit": "cookie",
            "chemist": "drugstore",
            "shop": "store",
            "football": "soccer",
            "autumn": "fall",
            "barrister": "attorney",
            "bill": "check",
            "caravan": "trailer",
            "cupboard": "closet",
            "diversion": "detour",
            "dustbin": "trash can",
            "jug": "pitcher",
            "lift": "elevator",
            "mad": "crazy",
            "maize": "corn",
            "maths": "math",
            "motorbike": "motorcycle",
            "motorway": "freeway",
            "nappy": "diaper",
            "pavement": "sidewalk",
            "post": "mail",
            "postman": "mailman",
            "pub": "bar",
            "rubber": "eraser",
            "solicitor": "attorney",
            "tax": "cab",
            "timetable": "schedule",
            "torch": "flashlight",
            "waistcoat": "vest",
            "windscreen": "windshield",
            "angry": "mad",
            "caretaker": "janitor",
            "cot": "crib",
            "curtains": "drapes",
            "engine": "motor",
            "garden": "yard",
            "handbag": "purse",
            "hoarding": "billboard",
            "ill": "sick",
            "interval": "intermission",
            "luggage": "baggage",
            "nowhere": "noplace",
            "optician": "optometrist",
            "queue": "line",
            "rubbish": "trash",
        }
        # Replacing the keys with values and vice versa for the custom vocab dictionary
        # And merging both of them
        vocab_diff = dict(
            (v, k) for k, v in difference_british_to_american.items()
        )
        vocab_diff.update(difference_british_to_american)

        """
        Gets the british to american english dictionary
        Gets the american to British english dictionary
        Merges both these dictionaries with the custom vocab dictionary.
        """
        
        american_british_fp = os.path.join(
        'transformations','text','utils','americanize_britishize_english', 'american_spellings.json'
        )
        with open(american_british_fp, "r") as fp:
            american_british_dict = json.load(fp)
        
        british_american_fp = os.path.join(
        'transformations','text','utils','americanize_britishize_english', 'british_spellings.json'
        )
        with open(british_american_fp, "r") as fp:
            british_american_dict = json.load(fp)

        self.final_dict = {
            **american_british_dict,
            **british_american_dict,
            **vocab_diff,
        }
            
    def generate(self, sentence: str):
        translated = britishize_americanize(sentence, self.final_dict)
        return ["".join(translated)]
