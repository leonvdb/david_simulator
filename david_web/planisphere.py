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
    english_name = db.Column(db.String(50), nullable=False) #TODO: Force to be capitalized
    german_name = db.Column(db.String(100), nullable=False) #TODO: Force to be capitalized
    description = db.Column(db.String)
    image = db.Column(db.String)
    items = db.relationship('Item', backref='location')

    paths = db.relationship('Room', 
    secondary=paths, 
    primaryjoin = (paths.c.destination_id == id),
    secondaryjoin = (paths.c.start_id == id),
    backref=db.backref('connections', lazy = 'dynamic'),
    lazy='dynamic'
    )

    def __init__(self, name, description,  english_name, german_name, image=None):
        self.name = name
        self.description = description
        self.image = image
        self.english_name = english_name
        self.german_name = german_name
        Room.instances.append(self)

class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True) 
    name = db.Column(db.String(50), nullable=False)
    english_name = db.Column(db.String(50), nullable=False) #TODO: Force to be capitalized
    german_name = db.Column(db.String(100), nullable=False) #TODO: Force to be capitalized
    takeable = db.Column(db.Boolean, nullable=False, default=False)
    location_id = db.Column(db.Integer, db.ForeignKey('room.id'))
    consume_lp = db.Column(db.Integer)
    consume_ap = db.Column(db.Integer)
    weapon_ap = db.Column(db.Integer)
    fight_ap = db.Column(db.Integer)
    fight_lp = db.Column(db.Integer)
    description_german = db.Column(db.String)
    description_english = db.Column(db.String)

    recipes = db.relationship('Item',
    secondary=recipes,
    primaryjoin = (recipes.c.ingredient_id == id),
    secondaryjoin = (recipes.c.final_item_id == id),
    backref=db.backref('ingredients', lazy = 'dynamic'),
    lazy='dynamic')


START = 'davids_room'

