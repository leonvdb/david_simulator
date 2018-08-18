from david_web.engine import match_room, Action, Room, get_inventory
from david_web import gamestate
from david_web import planisphere
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import secrets # pylint: disable-msg=E0611
from david_web.planisphere import db

import pytest

davids_room = match_room('davids_room')
kitchen = match_room('kitchen')
hallway = match_room('hallway')

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = secrets.database_uri

db.init_app(app)
db.app = app

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
    assert test_action.verbs_original == ['geh']
    assert test_action.verbs == ['go']
    assert test_action.directions_original == ['flur']
    assert test_action.directions == ['hallway']
    assert test_action.verb_count == 1
    assert test_action.object_count == 0
    test_action = Action(davids_room, 'nimm und iss die pflanze')
    result = test_action.determine_action()
    assert result == "\nDu hast zu viele Verben angegeben: nimm, iss.\nBitte schreib nur ein Verb statt 2!\n"
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
    result = test_action.determine_action()
    assert result == '\nDas angegebene objekt "pflanze" befindet sich nicht in diesem Bereich.\nLeider kannst du es also nicht aufnehmen...\n'
    test_action = Action(davids_room, 'nimm die pflanze')
    result = test_action.determine_action()
    assert 'plant' in get_inventory()
    assert planisphere.Item.query.filter_by(name='plant').first().location == None
    assert result == "\nDas Objekt \"Pflanze\" wurde deinem Inventar hinzugefügt!\n"
    test_action = Action(davids_room, 'gamestate')
    result = test_action.determine_action()
    assert 'Plant' in result
    test_action = Action(davids_room, 'nimm das Bett')
    result = test_action.determine_action()
    assert result == '\nDas angegebene objekt "Bett" kannst du leider nicht aufnehmen.\n'
    test_action = Action(davids_room, 'greif das Bett mit der Pflanze an!')
    result = test_action.determine_action()
    assert result == '\nDas Objekt "Pflanze" kannst du nicht als Waffe benutzen.\n'


def test_check_gamestate():
    test_action = Action(davids_room, 'gamestate')
    result = test_action.determine_action()
    print(">>>> enter current test")
    test_action = Action(kitchen, 'nimm das Messer')
    result = test_action.determine_action()
    print("Exit")
    assert 'knife' in get_inventory()
    assert planisphere.Item.query.filter_by(name='knife').first().amount_in_inventory == 1
    test_action = Action(davids_room, 'gamestate')
    result = test_action.determine_action()
    assert 'Knife' in result
    print("Gamestate", result)


def test_object_names():

    test_scene = Room("Name", "Description", ['test_path'], ['object_1', 'object_2'])
    assert test_scene.object_names == ['object_1', 'object_2']
