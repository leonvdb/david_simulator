from david_web import lexicon
from david_web import action_combinations
from david_web import gamestate
from textwrap import dedent

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
        self.verbs = []
        self.directions = []
        self.objects = []
        self.verb_count = 0
        self.direction_count = 0
        self.object_count = 0
        self.action_type = ''

    def scan_action(self):
        scanned_action = lexicon.scan(self.action)
        print(">>>> scanned_action:", scanned_action)

        for i in scanned_action:

            if i[0] == 'verb':
                self.verb_count += 1
                self.verbs.append(i[1])
            elif i[0] == 'direction':
                self.direction_count += 1
                self.directions.append(i[1])
            elif i[0] == 'object':
                self.object_count += 1
                self.objects.append(i[1])

    def determine_action(self):

        self.scan_action()

        if self.verb_count > 1:
            return self.error('too many verbs')
        elif self.verb_count < 1:
            return self.error('no verbs')
        elif self.direction_count > 1:
            return self.error('too many directions')
        elif 'go' in self.verbs:
            return self.go()
        elif 'consume' in self.verbs:
            return self.consume()
        elif 'attack' in self.verbs:
            return self.attack()
        elif 'take' in self.verbs:
            return self.take()
        else:
            pass


        #Errors for: verb_count != 1, direction_count > 1


    def error(self, reason):
        self.action_type = 'error'
        message = ''
        if reason == 'too many verbs':
            message = dedent(f"""
            Du hast zu viele Verben angegeben: {self.verbs}.
            Bitte schreib nur ein Verb statt {self.verb_count}!
            """)
        elif reason == 'no verbs':
            message = dedent(f"""
            Du hast kein bekanntes Verb in deinen Befehl geschrieben!
            Bitte gib ein Verb an!
            """)
        elif reason == 'too many directions':
            message = dedent(f"""
            Du hast zu viele Richtungen angegeben: {self.directions}.
            Bitte schreib nur eine Richtung statt {self.direction_count}
            """)
        elif reason == 'no direction':
            message = dedent(f"""
            Du hast keine bekannte Richtung in deinen Befehl geschrieben!
            Bitte gib eine Richtung an wenn du dich bewegen möchtest!
            """)
        elif reason == 'direction unavailable':
            message = dedent(f"""
            Du hast kannst das angegebene Ziel von hier nicht erreichen.
            """)
        elif reason == 'no take objects':
            message = dedent(f"""
            Du hast keinen bekannten Gegenstand angegeben.
            Bitte gib ein Objekt an das du aufnehmen möchtest.
            """)
        elif reason == 'too many take objects':
            message = dedent(f"""
            Du hast zu viele Objekte angegeben: {self.objects}.
            Du kannst nur ein Objekt gleichzeitig aufnehmen und nicht {self.object_count}
            """)
        elif reason == 'object not in room':
            message = dedent(f"""
            Das angegebene objekt \"{self.objects[0]}\" befindet sich nicht in diesem Bereich.
            Leider kannst du es also nicht aufnehmen...
            """)
        elif reason == 'object not takeable':
            message = dedent(f"""
            Das angegebene objekt \"{self.objects[0]}\" kannst du leider nicht aufnehmen.
            """)
        else:
            message = "Unknown Error."

        return message

    def take(self):
        self.action_type = 'take'
        if self.object_count < 1:
            return self.error('no take objects')
        elif self.object_count > 1:
            return self.error('too many take objects')
        elif self.objects[0] not in self.current_room.object_names:
            return self.error('object not in room')
        elif self.objects[0] not in action_combinations.takeable:
            return self.error('object not takeable')
        else:
            position_in_room = self.current_room.object_names.index(self.objects[0])
            self.current_room.object_names.pop(position_in_room)
            gamestate.inventory.append(self.objects[0])
            return dedent(f"""
            Das Objekt \"{self.objects[0]}\" wurde deinem Inventar hinzugefügt!
            """)

    def attack(self):
        pass

    def consume(self):
        pass

    def go(self):

        if self.directions:
            self.action_type = 'go'
            if self.directions[0] in list(self.current_room.paths.keys()):
                return self.current_room.get_path(self.directions[0])
            else:
                return self.error('direction unavailable')
        else:
            return self.error('no direction')



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

davids_room.add_object_names(['pflanze', 'scalpell', 'bett'])

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
