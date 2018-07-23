# pylint: disable-all

from app import db
from david_web.planisphere import Item, Room, Character

db.create_all()


davids_room = Room(name="Davids Room", description="Description of Davids Room")
hallway = Room(name="Hallway", description="Description of Hallway")
kitchen = Room(name="Kitchen", description="Description of Kitchen")
living_room = Room(name="Living Room", description="Description of Living Room")
leons_room = Room(name="Leons Room", description="Description of Leons Room")
fridge = Room(name="Fridge", description="Description of Fridge")
bathroom = Room(name="Bathroom", description="Description of Bathroom")
db.session.add(davids_room)
db.session.add(kitchen)
db.session.add(hallway)
db.session.add(living_room)
db.session.add(leons_room)
db.session.add(fridge)
db.session.add(bathroom)
db.session.commit()

hallway.connections.append(davids_room)
hallway.connections.append(bathroom)
hallway.connections.append(kitchen)
hallway.connections.append(living_room)
hallway.connections.append(leons_room)
kitchen.connections.append(fridge)
db.session.commit()



chair = Item(name="Chair", location=davids_room)
gas_bottle = Item(name="Gas bottle", location=living_room)
alarm_clock = Item(name="Alarm clock", location=leons_room)
candle = Item(name="Candle", location=fridge)
knife = Item(name="Knife", location=kitchen, weapon_ap=10)
bomb = Item(name="Bomb")
db.session.add(chair)
db.session.add(gas_bottle)
db.session.add(alarm_clock)
db.session.add(candle)
db.session.add(bomb)
db.session.commit()

bomb.ingredients.append(gas_bottle)
bomb.ingredients.append(candle)
bomb.ingredients.append(alarm_clock)
db.session.commit()

monster = Character(name="Hair Monster", location=bathroom, attack_points=20, life_points=140)
db.session.add(monster)
db.session.commit()