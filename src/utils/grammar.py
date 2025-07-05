NAMES = {
    'bicycle': 'bicycle',
    'person': 'people', 
    'bench': 'benches'
}

VOWELS = ['a', 'e', 'i', 'o', 'u']

def get_plural(name: str):
    plural = NAMES.get(name)
    return plural if plural else name + 's'

def get_article(count: int, name: str):
    first_letter = name[0]
    if count > 1:
        return count
    elif count == 1 and first_letter in VOWELS: 
        return 'an'
    return 'a'