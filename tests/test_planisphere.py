from david_web.planisphere import *
from david_web import gamestate


def test_room():
    gold = Room("GoldRoom",
                """This room has gold in it you can grab. There's a
                door to the north.""")
    assert gold.name == "GoldRoom"
    assert gold.paths == {}

def test_room_paths():
    center = Room("Center", "Test room in the center.")
    north = Room("North", "Test room in the north.")
    south = Room("South", "Test room in the south.")

    center.add_paths({'north': north, 'south': south})
    go_north = Action(center, 'geh north')
    assert go_north.determine_action() == north
    go_south = Action(center, 'geh south')
    assert go_south.determine_action() == south



def test_david_map():
    go_hallway = Action(davids_room, 'geh in den flur')
    assert go_hallway.determine_action() == hallway
    go_outside = Action(hallway, 'geh raus')
    assert go_outside.determine_action() == outside

def test_Action():

    test_action = Action(davids_room, 'geh in den flur')
    assert test_action.determine_action() == hallway
    test_action = Action(davids_room, 'geh in den flur')
    test_action.scan_action()
    assert test_action.verbs == ['go']
    assert test_action.directions == ['flur']
    assert test_action.verb_count == 1
    assert test_action.object_count == 0
    test_action = Action(davids_room, 'nimm und iss die pflanze')
    result = test_action.determine_action()
    assert result == "\nDu hast zu viele Verben angegeben: ['take', 'consume'].\nBitte schreib nur ein Verb statt 2!\n"
    test_action = Action(davids_room, 'die pflanze!!!')
    result = test_action.determine_action()
    assert result == '\nDu hast kein bekanntes Verb in deinen Befehl geschrieben!\nBitte gib ein Verb an!\n'
    test_action = Action(davids_room, 'geh in die Küche')
    result = test_action.determine_action()
    assert result == '\nDu hast kannst das angegebene Ziel von hier nicht erreichen.\n'

def test_take():
    test_action = Action(davids_room, 'nimm irgendwas')
    assert test_action.determine_action() == '\nDu hast keinen bekannten Gegenstand angegeben.\nBitte gib ein Objekt an das du aufnehmen möchtest.\n'
    test_action = Action(hallway, 'nimm die pflanze')
    assert test_action.determine_action() == "\nDas angegebene objekt \"pflanze\" befindet sich nicht in diesem Bereich.\nLeider kannst du es also nicht aufnehmen...\n"
    test_action = Action(davids_room, 'nimm die pflanze')
    result = test_action.determine_action()
    assert 'pflanze' in gamestate.inventory
    assert 'pflanze' not in davids_room.object_names
    assert result == "\nDas Objekt \"pflanze\" wurde deinem Inventar hinzugefügt!\n"
    test_action = Action(davids_room, 'nimm das Bett')
    result = test_action.determine_action()
    assert result == '\nDas angegebene objekt "bett" kannst du leider nicht aufnehmen.\n'

def test_object_names():

    test_scene = Room("Name", "Description")
    test_scene.add_object_names(['object_1', 'object_2'])
    assert test_scene.object_names == ['object_1', 'object_2']
