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


def test_lexicon_results():

    result = scan('ich eat pflanze in   davids_room')
    assert result == [('error', 'ich'), ('verb', 'consume'), ('object', 'pflanze'),
                      ('stop', 'in'), ('direction', 'davids_room')]
    result = scan('ich eat pflanze in   eingangsbereich')
    assert result == [('error', 'ich'), ('verb', 'consume'), ('object',
                                                              'pflanze'), ('stop', 'in'), ('direction', 'hallway')]
    result = scan('ich eat pflanze in   davids zimmer lololol!')
    assert result == [('error', 'ich'), ('verb', 'consume'), ('object', 'pflanze'),
                      ('stop', 'in'), ('direction', 'davids_room'), ('error', 'lololol')]
    result = scan('iss die pflanze auf!')
    assert result == [('verb', 'consume'), ('error', 'die'),
                      ('object', 'pflanze'), ('error', 'auf')]
