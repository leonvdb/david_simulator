from david_web import lexicon
from david_web import planisphere
from david_web.planisphere import db
from david_web import special_actions
from david_web import configuration
from config import secrets # pylint: disable-msg=E0611
from textwrap import dedent
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import sqlite3

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = secrets.database_uri

db.init_app(app)
db.app = app


class Room(object):
    instances = []

    def __init__(self, name, description, paths, object_names, db_id):
        self.name = name
        self.description = description
        self.paths = paths
        self.object_names = object_names
        self.id = db_id
        Room.instances.append(self)

    def get_path(self, action):
        return self.paths.get(action, None)



class ProcessDirector:
    instance_id = {}

    def __init__(self):
        self.allClasses = []

    def construct(self, id_name, name, description, paths, objects, db_id):
        instance = Room(name, description, paths, objects, db_id)
        self.allClasses.append(instance)
        ProcessDirector.instance_id[id_name] = instance


director = ProcessDirector()


def initalise_rooms():
    for i in planisphere.Room.query.all():
        paths = [j.name for j in i.connections.all()] + [j.name for j in i.paths.all()]
        objects = [k.name for k in planisphere.Item.query.filter_by(location=i).all()]
        
        director.construct(i.name, i.english_name, i.description, paths, objects, i.id)


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

    def __init__(self, current_room, action, data_dict):
        self.current_room = current_room
        self.data_dict = data_dict
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

    def determine_action(self, request_mode=None):

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
            return self.attack(request_mode)
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
        message = message.format(verbs=self.verbs_original, verb_count=self.verb_count,
                                 objects=self.objects_original, object_count=self.object_count,
                                 directions=self.directions_original, direction_count=self.direction_count)
        message = message.replace('[', '')
        message = message.replace(']', '')
        message = message.replace("'", "")
        self.data_dict['message'] = message 
        return self.data_dict

    def gamestate(self):
        lp = self.data_dict['character'].get('Health')
        ap = self.data_dict['character'].get('Attack_Points')
        states = self.data_dict['character'].get('States')
        inventory_list = []
        for k, v in self.data_dict['character']['Inventory'].items():
            query_item = planisphere.Item.query.filter_by(name=k).first()
            if v > 1:
                inventory_list.append(f'{query_item.english_name} ({v}x)')
            else: 
                inventory_list.append(query_item.english_name)

        invetory_str = ','.join(inventory_list)
        states_str = ','.join(states)

        message = dedent(f"""
        Lebenspunkte: {lp}
        Angriffspunkte: {ap}
        Inventar: {invetory_str}
        States: {states_str}
        """)
        self.data_dict['message'] = message 
        return self.data_dict

    def take(self):

        self.action_type = 'take'
        if self.object_count < 1:
            return self.error('no take objects')
        elif self.object_count > 1:
            return self.error('too many take objects')
        else:
            query_item = planisphere.Item.query.filter_by(name=self.objects[0]).first()

        if query_item.name not in self.current_room.object_names:
            return self.error('object not in room')
        else: 
            current_location = planisphere.Room.query.filter_by(id=self.current_room.id).first()
            query_item = planisphere.Item.query.filter_by(location=current_location, name=self.objects[0]).first()
        if query_item.id in self.data_dict['taken_items']:
            return self.error('object already taken')
        elif not query_item.takeable:
            return self.error('object not takeable')
        else:
            if query_item.name not in list(self.data_dict['character']['Inventory'].keys()):
                self.data_dict['character']['Inventory'][query_item.name] = 1
                self.data_dict['taken_items'].append(query_item.id)
            else:
                self.data_dict['character']['Inventory'][query_item.name] += 1
                self.data_dict['taken_items'].append(query_item.id)

            message = dedent(f"""
            Das Objekt \"{query_item.german_name}\" wurde deinem Inventar hinzugefügt!
            """)
            self.data_dict['message'] = message 
            return self.data_dict

    def attack(self, request_mode):
        self.action_type = 'attack'
        if self.object_count > 1 and self.with_action == False:
            return self.error('too many opponents')
        elif self.object_count > 2 and self.with_action:
            return self.error('too many opponents')
        elif self.object_count < 1:
            return self.error('no opponents')
        elif self.object_count == 1 and self.with_action:
            return self.error('weapon or opponent missing')
        #TODO: Add to manual - With action have to be phrase with the object first and the weapon
        else:
            query_opponent = planisphere.Item.query.filter_by(name=self.objects[0]).first()
        if query_opponent.location.english_name != self.current_room.name:
            return self.error('opponent not in room')
        elif not query_opponent.fight_lp:
            return self.error('object not attackable')

        else:
            if self.object_count == 2 and self.with_action == True:
                query_weapon = planisphere.Item.query.filter_by(name=self.objects[1]).first()
                if query_weapon.name not in self.data_dict['character']['Inventory']:
                    return self.error('weapon not in inventory')
                if not query_weapon.weapon_ap:
                    return self.error('not a valid weapon')
            if self.objects[0] in list(special_actions.attack.keys()):
                action_data = special_actions.attack.get(self.objects[0])
                if action_data.get('message') != 'none':
                    self.special_message = action_data.get('message')
            if query_opponent.name not in self.data_dict['opponents'].keys():
                self.data_dict['opponents'][query_opponent.name] = {'ap': query_opponent.fight_ap, 'lp': query_opponent.fight_lp}

            opp_data = self.data_dict['opponents'].get(self.objects[0])
            opp_lp = opp_data.get('lp')
            if opp_lp <= 0:
                return self.error('opponent already dead')

            else:
                opp_ap = opp_data.get('ap')
                david_ap = self.data_dict['character'].get('Attack_Points')
                if self.with_action:
                    weapon_attack = query_weapon.weapon_ap
                    david_ap = david_ap + weapon_attack
                david_lp = self.data_dict['character'].get('Health')
                self.data_dict['opponents'][self.objects[0]]['lp'] = opp_lp - david_ap
                self.data_dict['character']['Health'] = david_lp - opp_ap
                # get updated data
                opp_data = self.data_dict['opponents'].get(self.objects[0])
                opp_lp = opp_data.get('lp')
                david_lp = self.data_dict['character'].get('Health')
                message = f"""
                David im Kampf gegen {query_opponent.german_name}!
                David fügt {query_opponent.german_name} {david_ap} Schaden zu.
                {query_opponent.german_name} hat noch {opp_lp} Lebenspunkte.
                {query_opponent.german_name} fügt David {opp_ap} Schaden zu.
                David hat noch {david_lp} Lebenspunkte.
                """
                if opp_lp <= 0:
                    message = message + f"""
                    Du hast {query_opponent.german_name} besiegt!
                    """
                self.data_dict['message'] = message 
                return special_actions.special_actions(self,self.data_dict)

    def consume(self):
        self.action_type = 'consume'
        if self.object_count > 1:
            return self.error('too many food objects')
        elif self.object_count < 1:
            return self.error('no food objects')
        else:
            query_item = planisphere.Item.query.filter_by(name=self.objects[0]).first()

        if query_item.name not in self.data_dict['character']['Inventory']:
            if query_item.name not in self.current_room.object_names:
                return self.error('food object not available')
            else: 
                current_location = planisphere.Room.query.filter_by(id=self.current_room.id).first()
                query_item = planisphere.Item.query.filter_by(location=current_location, name=self.objects[0]).first()
            if query_item.id in self.data_dict['taken_items']:
                return self.error('food object not available')
        if not query_item.consume_lp and not query_item.consume_ap:
            return self.error('food object not consumable')
        else:
            if self.objects[0] in self.data_dict['character']['Inventory']:
                if self.data_dict['character']['Inventory'][self.objects[0]] > 1:
                    self.data_dict['character']['Inventory'][self.objects[0]] -= 1
                elif self.data_dict['character']['Inventory'][self.objects[0]] == 1:
                    del self.data_dict['character']['Inventory'][self.objects[0]]
            elif query_item.location.english_name == self.current_room.name and query_item.id not in self.data_dict['taken_items']: #TODO: Change from english_name to name when adapting Rooms to DB
                # TODO: Write test for this case
                self.data_dict['taken_items'].append(query_item.id)

            david_ap = self.data_dict['character'].get('Attack_Points')
            david_lp = self.data_dict['character'].get('Health')
            consumable_ap = query_item.consume_ap
            consumable_lp = query_item.consume_lp
            consumable_special = query_item.special
            

            message = f"""
            David konsumiert {query_item.german_name}.
            """
            if consumable_ap:
 
                self.data_dict['character']['Attack_Points'] = david_ap + consumable_ap
                message = message + f"""
                David bekommt {consumable_ap} Angriffspunkte von {query_item.german_name}.
                """
            if consumable_lp:
                self.data_dict['character']['Health'] = david_lp + consumable_lp
                message = message + f"""
                David bekommt {consumable_lp} Lebenspunkte von {query_item.german_name}.
                """
            if consumable_special:             
                self.data_dict['character']['States'].append(consumable_special)
                message = message + f"""
                David erhät neuen Status {consumable_special}.
                """
            self.data_dict['message'] = message 
            return self.data_dict

    def go(self):

        if self.directions:
            self.action_type = 'go'

            if self.directions[0] in self.current_room.paths:
                self.data_dict['room_log'].append(self.directions[0])
                self.data_dict['room_name'] = self.directions[0]
                query_room=planisphere.Room.query.filter_by(name=self.directions[0]).first()
                self.data_dict['message'] = query_room.description
                self.data_dict['image'] = query_room.image
                return special_actions.special_actions(self,self.data_dict)
            elif self.directions[0] == 'back' and len(self.data_dict['room_log']) > 1:
                self.data_dict['room_name'] = self.data_dict['room_log'][len(self.data_dict['room_log']) - 2]
                query_room=planisphere.Room.query.filter_by(name=self.data_dict['room_name']).first()
                self.data_dict['message'] = query_room.description
                self.data_dict['image'] = query_room.image
                return special_actions.special_actions(self,self.data_dict)
            elif self.directions[0] == 'back' and len(self.data_dict['room_log']) <= 1:
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
        else:
            query_item = planisphere.Item.query.filter_by(name=self.objects[0]).first()
            ingredients = query_item.ingredients.all()
        if not ingredients:
            return self.error('object not buildable')
        else:
 
            available = []
            missing = []
            for i in ingredients:
                if i.name in list(self.data_dict['character']['Inventory'].keys()) or i.location.name == self.current_room.name:
                    available.append(i.german_name)
                else:
                    missing.append(i.german_name)

            if not missing:

                if query_item.name not in list(self.data_dict['character']['Inventory'].keys()):
                    self.data_dict['character']['Inventory'][query_item.name] = 1
                    self.data_dict['taken_items'].append(query_item.id)
                else:
                    self.data_dict['character']['Inventory'][query_item.name] += 1
                    self.data_dict['taken_items'].append(query_item.id)

                for i in ingredients:

                    if i.name in self.data_dict['character']['Inventory']:
                        if self.data_dict['character']['Inventory'][i.name] > 1:
                            self.data_dict['character']['Inventory'][i.name] -= 1
                        elif self.data_dict['character']['Inventory'][i.name] == 1:
                            del self.data_dict['character']['Inventory'][i.name]
                    elif i.location.english_name == self.current_room.name and i.id not in self.data_dict['taken_items']: #TODO: Change from english_name to name when adapting Rooms to DB
                        # TODO: Write test for this case
                        self.data_dict['taken_items'].append(i.id)

                message = dedent(f"""
                Du hast erfolgreich das Objekt {self.objects_original[0]} gebaut!
                Es wurde deinem Inventar hinzugefügt!
                """)

                self.data_dict['message'] = message 
                return self.data_dict

            else:
                message =  dedent(f"""
                Du kannst das Objekt {self.objects_original[0]} noch nicht bauen.
                Dir fehlen noch folgende Objekte: {missing}.
                """)

                self.data_dict['message'] = message 
                return self.data_dict
