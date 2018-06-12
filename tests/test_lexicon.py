from david_web.lexicon import *
from david_web.planisphere import *
import pytest

def test_importing_names():
    # print("Hallway keys: ", directions_hallway)
    # print(">>>> All Directions: ", collect_names('paths'))
    with pytest.raises(LexcionError):
        print(">>>> All Directions: ", collect_names('test'))
    paths_collection = collect_names('paths')
    assert 'flur' in paths_collection
    objects_collection = collect_names('objects')
    assert 'pflanze' in objects_collection

def test_lexicon_results():

    result = scan('ich eat pflanze in   davidszimmer')
    assert result == [('error', 'ich'), ('verb', 'eat'), ('object', 'pflanze'), ('stop', 'in'), ('direction', 'davidszimmer')]
    result = scan('ich eat pflanze in   eingangsbereich')
    assert result == [('error', 'ich'), ('verb', 'eat'), ('object', 'pflanze'), ('stop', 'in'), ('direction', 'flur')]
    result = scan('ich eat pflanze in   davids zimmer lololol!')
    assert result == [('error', 'ich'), ('verb', 'eat'), ('object', 'pflanze'), ('stop', 'in'), ('direction', 'davidszimmer'), ('error','lololol')]
