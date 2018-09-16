from david_web import lexicon
from david_web import gamestate
from david_web import planisphere
from david_web.planisphere import db
from david_web import special_actions
from david_web import configuration
from config import secrets # pylint: disable-msg=E0611
from textwrap import dedent
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from werkzeug.contrib.cache import SimpleCache
import sqlite3

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = secrets.database_uri

db.init_app(app)
db.app = app

cache = SimpleCache()

class Room(object):
    instances = []

    def __init__(self, name, description, paths, object_names, db_id, image):
        self.name = name
        self.description = description
        self.paths = paths
        self.object_names = object_names
        self.id = db_id
        self.image = image
        Room.instances.append(self)

    def get_path(self, action):
        return self.paths.get(action, None)

    def get_image(self):
        image = cache.get(f"{self.name}_image")
        if not image:
            image = self.image
            cache.set(f"{self.name}_image", image, timeout=5 * 60)
        return image


class ProcessDirector:
    instance_id = {}

    def __init__(self):
        self.allClasses = []

    def construct(self, id_name, name, description, paths, objects, db_id, image):
        instance = Room(name, description, paths, objects, db_id, image)
        self.allClasses.append(instance)
        ProcessDirector.instance_id[id_name] = instance


director = ProcessDirector()


def initalise_rooms():
    for i in planisphere.Room.query.all():
        paths = [j.name for j in i.connections.all()] + [j.name for j in i.paths.all()]
        objects = [k.name for k in planisphere.Item.query.filter_by(location=i).all()]
        
        director.construct(i.name, i.english_name, i.description, paths, objects, i.id, i.image)


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

def get_inventory():
   
    # app = Flask(__name__)
    # app.config['SQLALCHEMY_DATABASE_URI'] = secrets.database_uri

    # db.init_app(app)
    # db.app = app

    # inventory_list = []
    # for i in planisphere.Item.query.filter(planisphere.Item.amount_in_inventory > 0).all():
    #     inventory_list.append(i.name)

    return gamestate.inventory


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
        inventory_list = []
        for k, v in gamestate.inventory.items():
            query_item = planisphere.Item.query.filter_by(name=k).first()
            if v > 1:
                inventory_list.append(f'{query_item.english_name} ({v}x)')
            else: 
                inventory_list.append(query_item.english_name)

        invetory_str = ','.join(inventory_list)

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
        else:
            query_item = planisphere.Item.query.filter_by(name=self.objects[0]).first()

        if query_item.name not in self.current_room.object_names:
            return self.error('object not in room')
        else: 
            current_location = planisphere.Room.query.filter_by(id=self.current_room.id).first()
            query_item = planisphere.Item.query.filter_by(location=current_location, name=self.objects[0]).first()
        if query_item.id in gamestate.taken_items:
            return self.error('object already taken')
        elif not query_item.takeable:
            return self.error('object not takeable')
        else:
            if query_item.name not in list(gamestate.inventory.keys()):
                gamestate.inventory[query_item.name] = 1
                gamestate.taken_items.append(query_item.id)
            else:
                gamestate.inventory[query_item.name] += 1
                gamestate.taken_items.append(query_item.id)

            return dedent(f"""
            Das Objekt \"{query_item.german_name}\" wurde deinem Inventar hinzugefügt!
            """)

    def attack(self):
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
                if query_weapon.name not in gamestate.inventory:
                    return self.error('weapon not in inventory')
                if not query_weapon.weapon_ap:
                    return self.error('not a valid weapon')
            if self.objects[0] in list(special_actions.attack.keys()):
                action_data = special_actions.attack.get(self.objects[0])
                if action_data.get('message') != 'none':
                    self.special_message = action_data.get('message')
                if action_data.get('special_action'):
                    special_actions.special_attack(self)
            if query_opponent.name not in gamestate.opponents.keys():
                gamestate.opponents[query_opponent.name] = {'ap': query_opponent.fight_ap, 'lp': query_opponent.fight_lp}

            opp_data = gamestate.opponents.get(self.objects[0])
            opp_lp = opp_data.get('lp')
            if opp_lp <= 0:
                return self.error('opponent already dead')

            else:
                opp_ap = opp_data.get('ap')
                david_ap = gamestate.character_stats.get('Attack_Points')
                if self.with_action:
                    weapon_attack = query_weapon.weapon_ap
                    david_ap = david_ap + weapon_attack
                david_lp = gamestate.character_stats.get('Health')
                gamestate.opponents[self.objects[0]]['lp'] = opp_lp - david_ap
                gamestate.character_stats['Health'] = david_lp - opp_ap
                # get updated data
                opp_data = gamestate.opponents.get(self.objects[0])
                opp_lp = opp_data.get('lp')
                david_lp = gamestate.character_stats.get('Health')
                message = f"""
                David im Kampf gegen {query_opponent.german_name}! """
                if self.special_message != None:
                    message = message + self.special_message
                message = message + f"""
                David fügt {query_opponent.german_name} {david_ap} Schaden zu.
                {query_opponent.german_name} hat noch {opp_lp} Lebenspunkte.
                {query_opponent.german_name} fügt David {opp_ap} Schaden zu.
                David hat noch {david_lp} Lebenspunkte.
                """
                if opp_lp <= 0:
                    message = message + f"""
                    Du hast {query_opponent.german_name} besiegt!
                    """
                return message

    def consume(self):
        self.action_type = 'consume'
        if self.object_count > 1:
            return self.error('too many food objects')
        elif self.object_count < 1:
            return self.error('no food objects')
        else:
            query_item = planisphere.Item.query.filter_by(name=self.objects[0]).first()

        if query_item.name not in gamestate.inventory:
            if query_item.name not in self.current_room.object_names:
                return self.error('food object not available')
            else: 
                current_location = planisphere.Room.query.filter_by(id=self.current_room.id).first()
                query_item = planisphere.Item.query.filter_by(location=current_location, name=self.objects[0]).first()
            if query_item.id in gamestate.taken_items:
                return self.error('food object not available')
        if not query_item.consume_lp and not query_item.consume_ap:
            return self.error('food object not consumable')
        else:
            if self.objects[0] in gamestate.inventory:
                if gamestate.inventory[self.objects[0]] > 1:
                    gamestate.inventory[self.objects[0]] -= 1
                elif gamestate.inventory[self.objects[0]] == 1:
                    del gamestate.inventory[self.objects[0]]
            elif query_item.location.english_name == self.current_room.name and query_item.id not in gamestate.taken_items: #TODO: Change from english_name to name when adapting Rooms to DB
                # TODO: Write test for this case
                gamestate.taken_items.append(query_item.id)

            david_ap = gamestate.character_stats.get('Attack_Points')
            david_lp = gamestate.character_stats.get('Health')
            consumable_ap = query_item.consume_ap
            consumable_lp = query_item.consume_lp
            consumable_special = query_item.special
            

            message = f"""
            David konsumiert {query_item.german_name}.
            """
            if consumable_ap:
 
                gamestate.character_stats['Attack_Points'] = david_ap + consumable_ap
                message = message + f"""
                David bekommt {consumable_ap} Angriffspunkte von {query_item.german_name}.
                """
            if consumable_lp:
                gamestate.character_stats['Health'] = david_lp + consumable_lp
                message = message + f"""
                David bekommt {consumable_lp} Lebenspunkte von {query_item.german_name}.
                """
            if consumable_special:             
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
        else:
            query_item = planisphere.Item.query.filter_by(name=self.objects[0]).first()
            ingredients = query_item.ingredients.all()
        if not ingredients:
            return self.error('object not buildable')
        else:
 
            available = []
            missing = []
            for i in ingredients:
                if i.name in list(gamestate.inventory.keys()) or i.location.name == self.current_room.name:
                    available.append(i.german_name)
                else:
                    missing.append(i.german_name)

            if not missing:

                if query_item.name not in list(gamestate.inventory.keys()):
                    gamestate.inventory[query_item.name] = 1
                    gamestate.taken_items.append(query_item.id)
                else:
                    gamestate.inventory[query_item.name] += 1
                    gamestate.taken_items.append(query_item.id)

                for i in ingredients:

                    if i.name in gamestate.inventory:
                        if gamestate.inventory[i.name] > 1:
                            gamestate.inventory[i.name] -= 1
                        elif gamestate.inventory[i.name] == 1:
                            del gamestate.inventory[i.name]
                    elif i.location.english_name == self.current_room.name and i.id not in gamestate.taken_items: #TODO: Change from english_name to name when adapting Rooms to DB
                        # TODO: Write test for this case
                        gamestate.taken_items.append(i.id)

                return dedent(f"""
                Du hast erfolgreich das Objekt {self.objects_original[0]} gebaut!
                Es wurde deinem Inventar hinzugefügt!
                """)
            else:
                return dedent(f"""
                Du kannst das Objekt {self.objects_original[0]} noch nicht bauen.
                Dir fehlen noch folgende Objekte: {missing}.
                """)
