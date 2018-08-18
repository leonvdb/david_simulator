from david_web.lexicon import *
from david_web.engine import *
import pytest


def test_importing_names():

    with pytest.raises(LexcionError):
        print(">>>> All Directions: ", collect_names('test'))
    paths_collection = collect_names('paths')
    assert 'hallway' in paths_collection
    objects_collection = collect_names('objects')
    assert 'bett' in objects_collection

def test_new_importing_names():
    all_items = create_resources('item', 'name')
    assert 'chair' in all_items

def test_lexicon_results():

    result = scan('bett')
    assert result == [('object','bed')]

    result = scan('ich eat pflanze in   davids_room')
    assert result == [('error', 'ich'), ('verb', 'consume'), ('object', 'plant'),
                      ('stop', 'in'), ('direction', 'davids_room')]
    result = scan('ich eat pflanze in   eingangsbereich')
    assert result == [('error', 'ich'), ('verb', 'consume'), ('object',
                                                              'plant'), ('stop', 'in'), ('direction', 'hallway')]
    result = scan('ich eat pflanze in   davids zimmer lololol!')
    assert result == [('error', 'ich'), ('verb', 'consume'), ('object', 'plant'),
                      ('stop', 'in'), ('direction', 'davids_room'), ('error', 'lololol')]
    result = scan('iss die pflanze auf!')
    assert result == [('verb', 'consume'), ('error', 'die'),
                      ('object', 'plant'), ('error', 'auf')]

    result = get_original_input('iss den eingangsbereich auf', 'verbs')
    assert result == ['iss']

    result = get_original_input('iss den Eingangsbereich auf', 'directions')
    assert result == ['Eingangsbereich']
