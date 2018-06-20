from david_web import engine
from david_web import lexicon_resources


class LexcionError(Exception):
    pass


def collect_names(category_name):
    all_collected_names = []
    instance_names = engine.Room.instances
    if category_name == 'paths':

        for instance in instance_names:

            all_collected_names.extend(list(instance.paths))

        return set(all_collected_names)

    elif category_name == 'objects':

        for instance in instance_names:

            all_collected_names.extend(instance.object_names)

        return set(all_collected_names)

    else:
        raise LexcionError(f"""
        Expected a different category. This category has been given:
        {category_name}
        """)


def clean(sentence):

    words = sentence.split()
    result = []
    for i in words:
        no_dots = i.replace(".", "")
        no_question = no_dots.replace("?", "")
        no_exclamation = no_question.replace("!", "")
        result.append(no_exclamation.lower())

    return result


def replace_synonyms(sentence):
    replaced = []
    clean_words = clean(sentence)
    position = 0
    for i in clean_words:
        if position < len(clean_words)-1:
            next_word = clean_words[position+1]
        else:
            next_word = None

        if i in lexicon_resources.two_word_names and next_word in lexicon_resources.two_word_names[i]:
            replace = lexicon_resources.two_word_names[i][next_word]
            replaced.append(replace)
            clean_words.pop(position+1)

        else:
            replace = lexicon_resources.synonyms_dict.get(i, i)
            replaced.append(replace)

        position += 1

    return replaced


def scan(sentence):
    # clean_words are used for scanning, original_words will be matched to type
    clean_words = replace_synonyms(sentence)
    direction_names = engine.directions_from_rooms
    object_names = list(engine.objects_from_rooms) + lexicon_resources.object_names
    verb_names = lexicon_resources.verb_names
    stop_names = lexicon_resources.stop_names
    matches_clean = []

    for i in clean_words:

        if i in direction_names:
            matches_clean.append(('direction', i))

        elif i in verb_names:
            matches_clean.append(('verb', i))

        elif i in stop_names:
            matches_clean.append(('stop', i))

        elif i in object_names:
            matches_clean.append(('object', i))

        else:
            try:
                matches_clean.append(('number', int(i)))
            except ValueError:
                matches_clean.append(('error', i))

    return matches_clean
