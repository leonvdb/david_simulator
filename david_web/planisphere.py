from david_web import lexicon
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


paths = db.Table('paths',
    db.Column('start_id', db.Integer, db.ForeignKey('room.id')),
    db.Column('destination_id', db.Integer, db.ForeignKey('room.id'))
    )

recipes = db.Table('recipes',
    db.Column('final_item_id', db.Integer, db.ForeignKey('item.id')),
    db.Column('ingredient_id', db.Integer, db.ForeignKey('item.id'))
    )

class Room(db.Model):
    instances = []
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    display_name = db.Column(db.String(50), nullable=False)
    description = db.Column(db.String)
    image = db.Column(db.String)
    items = db.relationship('Item', backref='location')
    characters = db.relationship('Character', backref='location')

    paths = db.relationship('Room', 
    secondary=paths, 
    primaryjoin = (paths.c.destination_id == id),
    secondaryjoin = (paths.c.start_id == id),
    backref=db.backref('connections', lazy = 'dynamic'),
    lazy='dynamic'
    )

    def __init__(self, name, description,  display_name, image=None):
        self.name = name
        self.description = description
        self.image = image
        self.display_name = display_name
        Room.instances.append(self)

class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True) 
    name = db.Column(db.String(50), nullable=False)
    display_name = db.Column(db.String(50), nullable=False)
    takeable = db.Column(db.Boolean, nullable=False, default=False)
    location_id = db.Column(db.Integer, db.ForeignKey('room.id'))
    consume_lp = db.Column(db.Integer)
    consume_ap = db.Column(db.Integer)
    weapon_ap = db.Column(db.Integer)
    special = db.Column(db.String(100))
    in_inventory = db.Column(db.Boolean, default=False)

    recipes = db.relationship('Item',
    secondary=recipes,
    primaryjoin = (recipes.c.ingredient_id == id),
    secondaryjoin = (recipes.c.final_item_id == id),
    backref=db.backref('ingredients', lazy = 'dynamic'),
    lazy='dynamic')


class Character(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), nullable=False)
    display_name = db.Column(db.String(50), nullable=False)
    location_id = db.Column(db.Integer, db.ForeignKey('room.id'), nullable=False)
    attack_points = db.Column(db.Integer)
    life_points = db.Column(db.Integer)

START = 'davids_room'

rooms = {'davids_room': {'name': 'Davids Room',
                         'description': 'Description of Davids ugly Room',
                         'paths': ['hallway'],
                         'objects': ['pflanze', 'scalpell', 'bett', 'salat', 'ingredient2']},
         'hallway':     {'name': 'Hallway',
                         'description': 'Description',
                         'paths': ['davids_room', 'leons_room', 'outside', 'living_room', 'kitchen', 'bathroom'],
                         'objects': ['pfand']},
         'leons_room':  {'name': 'Leons Room',
                         'description': 'Description of Leons Room',
                         'paths': ['hallway'],
                         'objects': ['wecker', 'leon', 'bett']},
         'outside':     {'name': 'Outside',
                         'description': 'Description of Outside',
                         'paths': ['hallway'],
                         'objects': []},
         'living_room': {'name': 'Living Room',
                         'description': 'Description of Living Room',
                         'paths': ['hallway'],
                         'objects': []},
         'kitchen':     {'name': 'Kitchen',
                         'description': 'Description of Kitchen',
                         'paths': ['hallway', 'fridge'],
                         'objects': ['pfeffi']},
         'bathroom':    {'name': 'Bathroom',
                         'description': 'Description of Bathroom',
                         'paths': ['hallway'],
                         'objects': ['monster', 'b12', 'toilette']},
         'fridge':      {'name': 'Fridge',
                         'description': 'Description of the Fridge',
                         'paths': ['kitchen'],
                         'objects': ['pfeffi', 'kerze']}

         }
