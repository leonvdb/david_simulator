from david_web.planisphere import *


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
    go_north = Action(center, 'north')
    assert go_north.go() == north
    go_south = Action(center, 'south')
    assert go_south.go() == south


def test_map():
    start = Room("Start", "You can go west and down a hole.")
    west = Room("Trees", "There are trees here, you can go east.")
    down = Room("Dungeon", "It's dark down here, you can go up.")

    start.add_paths({'west': west})
    west.add_paths({'east': start})
    go_west = Action(start, 'west')
    go_east_from_west = Action(go_west.go(), 'east')
    assert go_west.go() == west
    assert go_east_from_west.go() == start


def test_david_map():
    go_hallway = Action(davids_room, 'in den flur')
    assert go_hallway.go() == hallway
    suicide = Action(hallway, 'selbstmord')
    assert suicide.go() == death

def test_Action():

    test_action = Action(davids_room, 'in den flur')
    assert test_action.go() == hallway
