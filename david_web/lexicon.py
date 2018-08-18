from david_web import engine
from david_web import lexicon_resources
from david_web import planisphere
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import secrets # pylint: disable-msg=E0611
from david_web.planisphere import db


class LexcionError(Exception):
    pass

def create_resources(category_name, output_mode):
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = secrets.database_uri

    db.init_app(app)
    db.app = app

    name_list = []
    resource_table = planisphere.Item.query.all()
    if category_name == 'item':
        resource_table = planisphere.Item.query.all()
    elif category_name == 'room':
        resource_table = planisphere.Room.query.all()
    else:
        raise LexcionError(f"""
        Unknown category '{category_name}'""")
    
    if output_mode == 'name':
        for i in resource_table: 
            name_list.append(i.name.lower())
    if output_mode == 'english_name':
        for i in resource_table: 
            name_list.append(i.english_name.lower())
    if output_mode == 'german_name':
        for i in resource_table: 
            name_list.append(i.german_name.lower())

    return set(name_list)

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
        result.append(no_exclamation)

    return result


def replace_synonyms(sentence):
    replaced = []
    clean_words = clean(sentence)
    position = 0
    for i in clean_words:
        i = i.lower()
        if position < len(clean_words)-1:
            next_word = clean_words[position+1]
        else:
            next_word = None

        if i in lexicon_resources.two_word_names and next_word in lexicon_resources.two_word_names[i]:
            replace = lexicon_resources.two_word_names[i][next_word]
            replaced.append(replace)
            clean_words.pop(position+1)
        else:
            capitalized = i.capitalize()
            if i in list(lexicon_resources.synonyms_dict.keys()):
                replace = lexicon_resources.synonyms_dict.get(i)
            elif i in create_resources('item', 'english_name'):
                query = planisphere.Item.query.filter_by(english_name=capitalized).first()
                replace = query.name
            elif i in create_resources('room', 'english_name'):
                query = planisphere.Room.query.filter_by(english_name=capitalized).first()
                replace = query.name
            elif i in create_resources('item', 'german_name'):
                query = planisphere.Item.query.filter_by(german_name=capitalized).first()
                replace = query.name
            elif i in create_resources('room', 'german_name'):
                query = planisphere.Room.query.filter_by(german_name=capitalized).first()
                replace = query.name
            else: 
                replace = i
            
            replaced.append(replace)

        position += 1

    return replaced


def scan(sentence):
    # clean_words are used for scanning, original_words will be matched to type
    clean_words = replace_synonyms(sentence)
    #TODO: replace list(engine.directions/objects_from_rooms) with data from database. Then collect_names() and Room.Instances can be removed 
    direction_names = list(engine.directions_from_rooms) + lexicon_resources.direction_names
    object_names = list(create_resources('item', 'name')) + lexicon_resources.object_names
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


def get_original_input(sentence, mode):
    clean_original_words = clean(sentence)
    original_words_matched = []
    filtered_by_mode = []
    for i in clean_original_words:
        i_lower = i.lower()
        scanned = scan(i)[0]
        word_type = scanned[0]
        # if i_lower in list(lexicon_resources.synonyms_dict.keys()):

        #     original_words_matched.append((word_type, i))
        # elif i_lower == scanned[1]:
        #     original_words_matched.append((word_type, i))
        original_words_matched.append((word_type, i))

    if mode == 'objects':
        for i in original_words_matched:
            if i[0] == 'object':
                filtered_by_mode.append(i[1])
    elif mode == 'directions':
        for i in original_words_matched:
            if i[0] == 'direction':
                filtered_by_mode.append(i[1])
    elif mode == 'verbs':
        for i in original_words_matched:
            if i[0] == 'verb':
                filtered_by_mode.append(i[1])
    else:
        raise LexcionError(f"""
        Expected a different category. This category has been given:
        {mode}
        """)

    return filtered_by_mode
    # for clean clean_words
    # if in synonyms append to x_list with key
    #
    # for objects, directions if in key of x_list append to list object_original, etc.
