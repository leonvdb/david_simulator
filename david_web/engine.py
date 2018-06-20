from david_web import lexicon
from david_web import error_messages
from david_web import action_resources
from david_web import gamestate
from david_web import planisphere
from textwrap import dedent


class Room(object):

    instances = []

    def __init__(self, name, description, paths, object_names):
        self.name = name
        self.description = description
        self.paths = paths
        self.object_names = object_names
        Room.instances.append(self)

    def get_path(self, action):
        return self.paths.get(action, None)


class ProcessDirector:

    instance_id = {}

    def __init__(self):
        self.allClasses = []

    def construct(self, id_name, name, description, paths, objects):
        instance = Room(name, description, paths, objects)
        self.allClasses.append(instance)
        ProcessDirector.instance_id[id_name] = instance


director = ProcessDirector()


def initalise_rooms():

    for i in list(planisphere.rooms.keys()):
        i_data = planisphere.rooms.get(i)
        name = i_data.get('name')
        description = i_data.get('description')
        paths = i_data.get('paths')
        objects = i_data.get('objects')

        director.construct(i, name, description, paths, objects)


initalise_rooms()

objects_from_rooms = lexicon.collect_names('objects')
directions_from_rooms = lexicon.collect_names('paths')


def name_room(room):

    for key, value in ProcessDirector.instance_id.items():

        if value == room:
            return key


def match_Room(name):
    instance = ProcessDirector.instance_id.get(name)
    return instance


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
        self.with_action = False

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
            elif i[1] == 'with':
                self.with_action = True

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
        elif self.objects[0] not in action_resources.takeable:
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
        self.action_type = 'consume'
        if self.object_count > 1:
            return self.error('too many food objects')
        elif self.object_count < 1:
            return self.error('no food objects')
        elif self.objects[0] not in self.current_room.object_names and self.objects[0] not in gamestate.inventory:
            return self.error('food object not available')
        elif self.objects[0] not in list(action_resources.consumable_objects.keys()):
            return self.error('food object not consumable')
        else:
            if self.objects[0] in gamestate.inventory:
                position_in_inventory = gamestate.inventory.index(self.objects[0])
                gamestate.inventory.pop(position_in_inventory)
            elif self.objects[0] in self.current_room.object_names:
                position_in_room = self.current_room.object_names.index(self.objects[0])
                self.current_room.object_names.pop(position_in_room)
            david_ap = gamestate.character_stats.get('Attack_Points')
            david_lp = gamestate.character_stats.get('Health')
            consumable_data = action_resources.consumable_objects.get(self.objects[0])
            consumable_ap = consumable_data.get('ap')
            consumable_lp = consumable_data.get('lp')
            consumable_special = consumable_data.get('special')

            message = f"""
            David konsumiert {self.objects[0]}
            """
            if consumable_ap != 0:
                gamestate.character_stats['Attack_Points'] = david_ap + consumable_ap
                message = message + f"""
                David bekommt {consumable_ap} Angriffspunkte von {self.objects[0]}.
                """
            if consumable_lp != 0:
                gamestate.character_stats['Health'] = david_lp + consumable_lp
                message = message + f"""
                David bekommt {consumable_lp} Lebenspunkte von {self.objects[0]}.
                """
            if consumable_special != None:
                gamestate.states.append(consumable_special)
                message = message + f"""
                David erhät neuen Status {consumable_special}.
                """
            return message

    def go(self):

        if self.directions:
            self.action_type = 'go'

            if self.directions[0] in self.current_room.paths:
                return self.directions[0]
            else:
                return self.error('direction unavailable')
        else:
            return self.error('no direction')
