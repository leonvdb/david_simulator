class Room(object):

    instances = []

    def __init__(self, name, description):
        self.name = name
        self.description = description
        self.paths = {}
        self.object_names = []
        Room.instances.append(self)

    def get_path(self, action):
        return self.paths.get(action, None)


    def add_paths(self, paths):
        self.paths.update(paths)

    def add_object_names(self, object_name_list):
        self.object_names.extend(object_name_list)

class Action(object):

    def __init__(self, current_room, action):
        self.current_room = current_room
        self.action = action

    def parse_action(self):

        parsed_action = self.action
        return parsed_action


    def go(self):

        return self.current_room.get_path(self.parse_action())

davids_room = Room("Davids Room",
"""
Description of Davids ugly room
""")

hallway = Room("Hallway",
"""
Description of the Hallway
""")

leons_room = Room("Leons Room",
"""
Description of Leons Room
""")


outside = Room("Outside",
"""
Description of Outside
""")

living_room = Room("Living Room",
"""
Description of Living Room
""")

kitchen = Room("Kitchen",
"""
Description of Kitchen
""")

bathroom = Room("Bathroom",
"""
Description of Bathroom
""")

death = Room("Death",
"""
Description of Death
""")

davids_room.add_paths({
    'flur' : hallway
})

davids_room.add_object_names(['pflanze', 'scalpell'])

hallway.add_paths({
    'davidszimmer' : davids_room,
    'leonszimmer' : leons_room,
    'raus' : outside,
    'wohnzimmer' : living_room,
    'küche' : kitchen,
    'badezimmer' : bathroom

})

leons_room.add_paths({
    'flur' : hallway
})

outside.add_paths({
    'haus' : hallway
})

living_room.add_paths({
    'flur': hallway
})

kitchen.add_paths({
    'flur': hallway
})

bathroom.add_paths({
    'flur': hallway
})


START = 'davids_room'


def load_room(name):

    return globals().get(name)

def name_room(room):

    for key, value in globals().items():
        if value == room:
            return key
