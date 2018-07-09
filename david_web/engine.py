from david_web import lexicon
from david_web import action_resources
from david_web import gamestate
from david_web import planisphere
from david_web import special_actions
from david_web import configuration
from textwrap import dedent
import sqlite3


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
                


def match_room(name):
    instance = ProcessDirector.instance_id.get(name)
    return instance


class Action(object):

    def __init__(self, current_room, action):
        self.current_room = current_room
        self.action = action
        self.verbs = []
        self.verbs_original = lexicon.get_original_input(action, 'verbs')
        self.directions = []
        self.directions_original = lexicon.get_original_input(action, 'directions')
        self.objects = []
        self.objects_original = lexicon.get_original_input(action, 'objects')
        self.verb_count = 0
        self.direction_count = 0
        self.object_count = 0
        self.action_type = ''
        self.with_action = False
        self.special_message = None

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
        elif 'build' in self.verbs:
            return self.build()
        else:
            pass

    def error(self, reason):
        self.action_type = 'error'
        conn = sqlite3.connect(configuration.error_messages_path)
        c = conn.cursor()
        c.execute("SELECT message FROM error_messages WHERE key =:key;", {'key': reason})
        tuple_from_db = c.fetchone()
        message = tuple_from_db[0]
        conn.close()
        message = dedent(message)
        # message = dedent(error_messages.return_error_message(reason))
        message = message.format(verbs=self.verbs_original, verb_count=self.verb_count,
                                 objects=self.objects_original, object_count=self.object_count,
                                 directions=self.directions_original, direction_count=self.direction_count)
        message = message.replace('[', '')
        message = message.replace(']', '')
        message = message.replace("'", "")
        return message

    def gamestate(self):
        lp = gamestate.character_stats.get('Health')
        ap = gamestate.character_stats.get('Attack_Points')
        inventory_no_tuples = []
        for i in gamestate.inventory:
            if isinstance(i[1], int):
                inventory_no_tuples.append(f'{i[1]} {i[0]}')
            else:
                inventory_no_tuples.append(i)

        invetory_str = ','.join(inventory_no_tuples)

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
            if self.objects[0] not in gamestate.inventory:
                gamestate.inventory.append(self.objects[0])
            else:
                tuple_in_inventory = False
                for i in gamestate.inventory:
                    if i[0] == self.objects[0]:
                        i[1] += 1
                        tuple_in_inventory = True
                if not tuple_in_inventory:
                    position_in_inventory = gamestate.inventory.index(self.objects[0])
                    gamestate.inventory.pop(position_in_inventory)
                    gamestate.inventory.append((self.objects[0], 2))

            return dedent(f"""
            Das Objekt \"{self.objects[0]}\" wurde deinem Inventar hinzugefügt!
            """)

    def attack(self):
        self.action_type = 'attack'
        if self.object_count > 1 and self.with_action == False:
            return self.error('too many opponents')
        elif self.object_count > 2 and self.with_action:
            return self.error('too many opponents')
        elif self.object_count < 1:
            return self.error('no opponents')
        elif self.objects[0] not in self.current_room.object_names:
            return self.error('opponent not in room')
        elif self.objects[0] not in list(gamestate.opponents.keys()):
            return self.error('object not attackable')

        else:
            if self.object_count == 2 and self.with_action == True:
                if self.objects[1] not in list(action_resources.weapons.keys()):
                    return self.error('not a valid weapon')
            if self.objects[0] in list(special_actions.attack.keys()):
                action_data = special_actions.attack.get(self.objects[0])
                if action_data.get('message') != 'none':
                    self.special_message = action_data.get('message')
                if action_data.get('special_action') == True:
                    special_actions.special_attack(self)

            opp_data = gamestate.opponents.get(self.objects[0])
            opp_lp = opp_data.get('lp')
            if opp_lp <= 0:
                return self.error('opponent already dead')

            else:
                opp_ap = opp_data.get('ap')
                david_ap = gamestate.character_stats.get('Attack_Points')
                if self.with_action:
                    weapon_attack = action_resources.weapons.get(self.objects[1])
                    david_ap = david_ap + weapon_attack
                david_lp = gamestate.character_stats.get('Health')
                gamestate.opponents[self.objects[0]]['lp'] = opp_lp - david_ap
                gamestate.character_stats['Health'] = david_lp - opp_ap
                # get updated data
                opp_data = gamestate.opponents.get(self.objects[0])
                opp_lp = opp_data.get('lp')
                david_lp = gamestate.character_stats.get('Health')
                message = f"""
                David im Kampf gegen {self.objects[0]}! """
                if self.special_message != None:
                    message = message + self.special_message
                message = message + f"""
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
        object_stacked = False
        if self.object_count > 1:
            return self.error('too many food objects')
        elif self.object_count < 1:
            return self.error('no food objects')
        elif self.objects[0] not in self.current_room.object_names and self.objects[0] not in gamestate.inventory:
            for i in gamestate.inventory:
                if i[0] == self.objects[0]:
                    object_stacked = True
            if object_stacked == False:
                return self.error('food object not available')
        if self.objects[0] not in list(action_resources.consumable_objects.keys()):
            return self.error('food object not consumable')
        else:
            if self.objects[0] in gamestate.inventory:
                position_in_inventory = gamestate.inventory.index(self.objects[0])
                gamestate.inventory.pop(position_in_inventory)
            elif self.objects[0] in self.current_room.object_names:
                position_in_room = self.current_room.object_names.index(self.objects[0])
                self.current_room.object_names.pop(position_in_room)

            elif object_stacked == True:
                for i in gamestate.inventory:
                    if isinstance(i[1], int):
                        position_in_inventory = gamestate.inventory.index(i)
                        if i[1] > 2:
                            i[1] -= 1
                        else:
                            gamestate.inventory.pop(position_in_inventory)
                            gamestate.inventory.append(i[0])

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
                gamestate.room_log.append(self.directions[0])
                return self.directions[0]
            elif self.directions[0] == 'back' and len(gamestate.room_log) > 1:
                return gamestate.room_log[len(gamestate.room_log) - 2]
            elif self.directions[0] == 'back' and len(gamestate.room_log) <= 1:
                return self.error('cannot go back')

            else:
                return self.error('direction unavailable')
        else:
            return self.error('no direction')

    def build(self):
        self.action_type = 'build'
        if self.object_count < 1:
            return self.error('no build objects')
        elif self.object_count > 1:
            return self.error('too many build objects')
        elif self.objects[0] not in list(action_resources.buildable_objects.keys()):
            return self.error('object not buildable')
        elif self.objects[0] in list(action_resources.buildable_objects.keys()):
            ingredients = action_resources.buildable_objects.get(self.objects[0])
            available = []
            missing = []
            for i in ingredients:

                if i in gamestate.inventory or i in self.current_room.object_names:
                    available.append(i)
                else:
                    missing.append(i)

            if available == ingredients:
                gamestate.inventory.append(self.objects[0])
                for i in ingredients:

                    if i in gamestate.inventory:
                        inventory_position = gamestate.inventory.index(i)
                        gamestate.inventory.pop(inventory_position)
                    elif i in self.current_room.object_names:
                        position_in_room = self.current_room.object_names.index(i)
                        self.current_room.object_names.pop(position_in_room)

                return dedent(f"""
                Du hast erfolgreich das Objekt {self.objects[0]} gebaut!
                Es wurde deinem Inventar hinzugefügt!
                """)
            else:
                return dedent(f"""
                Du kannst das Objekt {self.objects[0]} noch nicht bauen.
                Dir fehlen noch folgende Objekte: {missing}.
                """)
