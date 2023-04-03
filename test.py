import random

test_dict = {"laugh": ["L", "LMAO", "XD", "LOL", "XDDDDD", "ECKS DEE"], "insult": ["fucker", "idiot", "asshole", "stupid"], "fuckup":  ["RUH ROH", "oops", "oopsies", "o no", "oh noes"], "exclaim": ["WOW", "OMG", "OML", "WTF"]}

# Function to get random thing from lang
def get_random(dict_in: dict, field: str):

    # Return random choice from field
    return random.choice(dict_in[field])

print(get_random(test_dict, "exclaim"))