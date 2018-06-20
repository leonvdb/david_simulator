from david_web.engine import *
from david_web import gamestate
import pytest

davids_room = match_Room('davids_room')

hallway = match_Room('hallway')


@pytest.fixture()
def reset():
    pass


def test_david_map():
    go_hallway = Action(davids_room, 'geh in den flur')
    assert go_hallway.determine_action() == 'hallway'
    go_outside = Action(hallway, 'geh raus')
    assert go_outside.determine_action() == 'outside'


def test_Action():

    test_action = Action(davids_room, 'geh in den flur')
    assert test_action.determine_action() == 'hallway'
    test_action = Action(davids_room, 'geh in den flur')
    test_action.scan_action()
    assert test_action.verbs == ['go']
    assert test_action.directions == ['hallway']
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
    test_action = Action(davids_room, 'greif das bett mit dem scalpell an')
    result = test_action.determine_action()
    assert test_action.with_action == True


def test_take():
    test_action = Action(davids_room, 'nimm irgendwas')
    assert test_action.determine_action(
    ) == '\nDu hast keinen bekannten Gegenstand angegeben.\nBitte gib ein Objekt an das du aufnehmen möchtest.\n'
    test_action = Action(hallway, 'nimm die pflanze')
    assert test_action.determine_action(
    ) == "\nDas angegebene objekt \"pflanze\" befindet sich nicht in diesem Bereich.\nLeider kannst du es also nicht aufnehmen...\n"
    test_action = Action(davids_room, 'nimm die pflanze')
    result = test_action.determine_action()
    assert 'pflanze' in gamestate.inventory
    assert 'pflanze' not in davids_room.object_names
    assert result == "\nDas Objekt \"pflanze\" wurde deinem Inventar hinzugefügt!\n"
    test_action = Action(davids_room, 'nimm das Bett')
    result = test_action.determine_action()
    assert result == '\nDas angegebene objekt "bett" kannst du leider nicht aufnehmen.\n'


def test_check_gamestate(reset):
    test_action = Action(davids_room, 'gamestate')
    result = test_action.determine_action()


def test_object_names():

    test_scene = Room("Name", "Description", ['test_path'], ['object_1', 'object_2'])
    assert test_scene.object_names == ['object_1', 'object_2']
