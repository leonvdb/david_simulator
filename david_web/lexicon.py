from david_web import planisphere

class LexcionError(Exception):
    pass

def collect_names(category_name):
    all_direction_names = []
    instance_names = planisphere.Room.instances
    if category_name == 'paths':

        for instance in instance_names:

            all_direction_names.extend(list(instance.paths))
    else:
        raise LexcionError(f"""
        Expected a different category. This category has been given:
        {category_name}
        """)

    return set(all_direction_names)

#TESTING GOING ON HERE!
directions_imported = collect_names('paths')
directions_synonyms = ['test']

direction_names = list(directions_imported) + directions_synonyms
####################

def clean(sentence):

    words = sentence.split()
    result = []
    for i in words:
        no_dots = i.replace(".", "")
        no_question = no_dots.replace("?", "")
        no_exclamation = no_question.replace("!", "")
        result.append(no_exclamation.lower())


    return result

def scan(sentence):
    #clean_words are used for scanning, original_words will be matched to type
    original_words = sentence.split()
    clean_words = clean(sentence)

    directions_imported = collect_names('paths')
    directions_synonyms = ['test']

    direction_names = list(directions_imported) + directions_synonyms

    verb_names = ['go', 'kill', 'eat']
    stop_names = ['the', 'in', 'of', 'to']
    noun_names = ['bear', 'princess']
    matches = []

    for i, j in zip(original_words, clean_words):

        if j in direction_names:
            matches.append(('direction', i))

        elif j in verb_names:
            matches.append(('verb', i))

        elif j in stop_names:
            matches.append(('stop', i))

        elif j in noun_names:
            matches.append(('noun', i))

        else:
            try:
                matches.append(('number', int(i)))
            except ValueError:
                matches.append(('error', i))

    return matches
