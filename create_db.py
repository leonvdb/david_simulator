from app import db
from david_web.planisphere import Item, Room, paths, recipes 
from sqlalchemy.exc import ProgrammingError


db_creation = False
# pylint: disable-all

def drop_table(target):
    try:
        target.drop(db.engine)
    except ProgrammingError:
        pass

def set_up():
    print("Database set up initialzing.")
    db.engine.execute("""SELECT pg_terminate_backend(pg_stat_activity.pid)
                         FROM pg_stat_activity
                         WHERE pg_stat_activity.datname = 'david_web'
                         AND pid <> pg_backend_pid();""")
    
    drop_table(paths)
    drop_table(recipes)
    drop_table(Item.__table__)
    drop_table(Room.__table__)
    db.session.commit()

    db.create_all()


    davids_room = Room(name="davids_room", english_name = "Davids Room", german_name="Davids Zimmer", description="Description of Davids Room", image = "/static/images/davids_room.jpg")
    hallway = Room(name="hallway", english_name = "Hallway", german_name="Flur", description="Description of Hallway", image="/static/images/hallway.jpg")
    kitchen = Room(name="kitchen", english_name = "Kitchen", german_name="Küche", description="Description of Kitchen", image = "/static/images/kitchen.jpg")
    living_room = Room(name="living_room", english_name = "Living Room", german_name="Wohnzimmer", description="Description of Living Room", image="/static/images/living_room.jpg")
    leons_room = Room(name="leons_room", english_name = "Leons Room", german_name="Leons Zimmer", description="Description of Leons Room", image="/static/images/leons_room.jpg")
    fridge = Room(name="fridge", english_name = "Fridge", german_name="Kühlschrank", description="Description of Fridge", image="/static/images/fridge.jpg")
    bathroom = Room(name="bathroom", english_name = "Bathroom", german_name="Badezimmer", description="Description of Bathroom", image="/static/images/bathroom.jpg")
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
    fridge.connections.append(hallway)
    db.session.commit()



    chair = Item(name="chair", english_name="Chair", german_name="Sessel", location=davids_room)
    gas_bottle = Item(name="gas_bottle", english_name="Gas Bottle", german_name="Gasflasche", location=living_room, takeable=True)
    alarm_clock = Item(name="alarm_clock", english_name="Alarm Clock", german_name="Wecker", location=leons_room, takeable=True)
    candle = Item(name="candle", english_name="Candle", german_name="Kerze", location=fridge, takeable=True)
    knife = Item(name="knife", english_name="Knife", german_name="Brotmesser", location=kitchen, weapon_ap=10, consume_lp=-100, takeable=True)
    bomb = Item(name="bomb", english_name="Bomb", german_name="Bombe")
    plant = Item(name="plant", english_name="Plant", german_name="Pflanze", location=davids_room, takeable=True, consume_lp=10, special='vegan')
    monster = Item(name="monster", english_name="Hair Monster", german_name="Haar Monster", location=bathroom, fight_ap=20, fight_lp=140)
    bed = Item(name="bed", english_name="Bed", german_name="Bett", location=davids_room, fight_ap=0, fight_lp=10)
    pfeffi = Item(name="pfeffi", english_name="Pfeffi", german_name="Pfeffi", location=davids_room, consume_lp=5, consume_ap=5, special='drunk', takeable=True)
    b12 = Item(name="b12", english_name="B12", german_name="B12", location=bathroom, takeable=True, consume_lp=20, consume_ap=10)
    pfeffi2 = Item(name="pfeffi", english_name="Pfeffi", german_name="Pfeffi", location=kitchen, consume_lp=5, consume_ap=5, special='drunk', takeable=True)
    pfeffi3 = Item(name="pfeffi", english_name="Pfeffi", german_name="Pfeffi", location=fridge, consume_lp=5, consume_ap=5, special='drunk', takeable=True)
    paint = Item(name="paint", english_name="Paint", german_name="Farbe", location=davids_room, takeable=True)

    db.session.add(chair)
    db.session.add(gas_bottle)
    db.session.add(alarm_clock)
    db.session.add(candle)
    db.session.add(bomb)
    db.session.add(plant)
    db.session.add(monster)
    db.session.add(bed)
    db.session.add(pfeffi)
    db.session.add(b12)
    db.session.add(pfeffi2)
    db.session.add(pfeffi3)
    db.session.commit()

    bomb.ingredients.append(gas_bottle)
    bomb.ingredients.append(candle)
    bomb.ingredients.append(alarm_clock)
    db.session.commit()
    db.session.close()
    print("Database succesfully created.")

set_up()