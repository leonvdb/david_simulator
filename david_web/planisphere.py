from david_web import lexicon
from david_web import error_messages
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
        elif 'gamestate' in self.verbs:
            return self.gamestate()
        else:
            pass

        # Errors for: verb_count != 1, direction_count > 1

    def error(self, reason):
        self.action_type = 'error'

        message = dedent(error_messages.return_error_message(reason))
        message = message.format(verbs=self.verbs, verb_count=self.verb_count,
                                 objects=self.objects, object_count=self.object_count,
                                 directions=self.directions, direction_count=self.direction_count)

        return message

    def gamestate(self):
        lp = gamestate.character_stats.get('Health')
        ap = gamestate.character_stats.get('Attack_Points')
        invetory_str = ','.join(gamestate.inventory)

        return dedent(f"""
        Lebenspunkte: {lp}
        Angriffspunkte: {ap}
        Inventar: {invetory_str}
        """)

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
        self.action_type = 'attack'
        if self.object_count > 1:
            return self.error('too many opponents')
        elif self.object_count < 1:
            return self.error('no opponents')
        elif self.objects[0] not in self.current_room.object_names:
            return self.error('opponent not in room')
        elif self.objects[0] not in list(gamestate.opponents.keys()):
            return self.error('object not attackable')
        else:

            opp_data = gamestate.opponents.get(self.objects[0])
            opp_lp = opp_data.get('lp')
            if opp_lp <= 0:
                return self.error('opponent already dead')

            else:
                opp_ap = opp_data.get('ap')
                david_ap = gamestate.character_stats.get('Attack_Points')
                david_lp = gamestate.character_stats.get('Health')
                gamestate.opponents[self.objects[0]]['lp'] = opp_lp - david_ap
                gamestate.character_stats['Health'] = david_lp - opp_ap
                # get updated data
                opp_data = gamestate.opponents.get(self.objects[0])
                opp_lp = opp_data.get('lp')
                david_lp = gamestate.character_stats.get('Health')
                message = f"""
                David im Kampf gegen {self.objects[0]}!
                David fügt {self.objects[0]} {david_ap} Schaden zu.
                {self.objects[0]} hat noch {opp_lp} Lebenspunkte.
                {self.objects[0]} fügt David {opp_ap} Schaden zu.
                David hat noch {david_lp} Lebenspunkte.
                """
                if opp_lp <= 0:
                    message = message + f"""
                    Du hast {self.objects[0]} besiegt!
                    """
                return message

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
    'flur': hallway
})

davids_room.add_object_names(['pflanze', 'scalpell', 'bett'])

hallway.add_paths({
    'davidszimmer': davids_room,
    'leonszimmer': leons_room,
    'raus': outside,
    'wohnzimmer': living_room,
    'küche': kitchen,
    'badezimmer': bathroom

})

leons_room.add_paths({
    'flur': hallway
})

outside.add_paths({
    'haus': hallway
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

bathroom.add_object_names(['monster', 'b12', 'toilette'])


START = 'davids_room'
objects_from_rooms = lexicon.collect_names('objects')
directions_from_rooms = lexicon.collect_names('paths')


def load_room(name):

    return globals().get(name)


def name_room(room):

    for key, value in globals().items():
        if value == room:
            return key
