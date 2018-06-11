from david_web.lexicon import *
import pytest

def test_importing_locations():
    # print("Hallway keys: ", directions_hallway)
    # print(">>>> All Directions: ", collect_names('paths'))
    with pytest.raises(LexcionError):
        print(">>>> All Directions: ", collect_names('test'))
    print(">>>> Directions", directions_imported)
    print(">>>> All Directions", direction_names)
