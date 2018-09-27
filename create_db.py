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


    davids_room = Room(name="davids_room", english_name = "Davids Room", german_name="Davids Zimmer", description="Du befindest dich in Davids Zimmer. Trautes Heim.", image = "/static/images/davids_room.jpg")
    hallway = Room(name="hallway", english_name = "Hallway", german_name="Flur", description="Du betrittst den Flur", image="/static/images/hallway.jpg")
    kitchen = Room(name="kitchen", english_name = "Kitchen", german_name="Küche", description="Du betrittst die Küche", image = "/static/images/kitchen.jpg")
    living_room = Room(name="living_room", english_name = "Living Room", german_name="Wohnzimmer", description="Du betrittst das Wohnzimmer, bzw. Mareks Zimmer, bzw. Pascals Zimmer, bzw. Miriams Zimmer. Wer wohnt hier?", image="/static/images/living_room.jpg")
    leons_room = Room(name="leons_room", english_name = "Leons Room", german_name="Leons Zimmer", description="Du betrittst Leons Zimmer", image="/static/images/leons_room.jpg")
    fridge = Room(name="fridge", english_name = "Fridge", german_name="Kühlschrank", description="Du öffnest den Kühlschrank", image="/static/images/fridge.jpg")
    bathroom = Room(name="bathroom", english_name = "Bathroom", german_name="Badezimmer", description="Du betrittst das Badezimmer", image="/static/images/bathroom.jpg")
    staircase = Room(name="staircase", english_name="Staircase", german_name="Treppenhaus", description="Du betrittst das Treppenhaus. Es riecht nach Zigarettenrauch und Thai Food.", image="/static/images/staircase.jpg")
    yard = Room(name="yard", english_name="Yard", german_name="Innenhof", description="Du betritts den Innenhof. Ein paar Ratten zwitschern und sonst ist stille. Was für ein idyllischer Abend.", image="/static/images/yard.jpg")
    spaeti = Room(name="spaeti", english_name="Spaeti", german_name="Späti", description="Du betritts den Späti. Der Spätimann scheint nicht hier zu sein und um hier etwas zu nehmen ohne zu bezahlen müsstet du schon recht betrunken sein. Es sei denn es handelt sich um eine Avocado.", image="/static/images/spaeti.jpg")
    balcony = Room(name="balcony", english_name="Balcony", german_name="Balkon", description="Du betrittst den Balkon. Unter dir siehst du ein paar Leute im Koy sitzen... ", image="/static/images/balcony.jpg")
    cupboard = Room(name="cupboard", english_name="Cupboard", german_name="Schrank", description="Du öffnest den Küchenschrank.", image="static/images/cupboard.jpg")
    shelf = Room(name="shelf", english_name="Shelf", german_name="Regal", description="Du öffnest das Regalfach.", image="/static/images/shelf.jpg")


    db.session.add(davids_room)
    db.session.add(kitchen)
    db.session.add(hallway)
    db.session.add(living_room)
    db.session.add(leons_room)
    db.session.add(fridge)
    db.session.add(bathroom)
    db.session.add(staircase)
    db.session.add(yard)
    db.session.add(spaeti)
    db.session.add(balcony)
    db.session.add(cupboard)
    db.session.add(shelf)
    db.session.commit()

    hallway.connections.append(davids_room)
    hallway.connections.append(bathroom)
    hallway.connections.append(kitchen)
    hallway.connections.append(living_room)
    hallway.connections.append(leons_room)
    hallway.connections.append(staircase)
    staircase.connections.append(yard)
    staircase.connections.append(spaeti)
    kitchen.connections.append(fridge)
    kitchen.connections.append(cupboard)
    living_room.connections.append(shelf)
    davids_room.connections.append(balcony)
    db.session.commit()



    chair = Item(name="chair", english_name="Chair", german_name="Sessel", location=davids_room, description_german="Ein schicker Sessel! Perfekt für Netflix und Insta!")
    gas_bottle = Item(name="gas_bottle", english_name="Gas Bottle", german_name="Gasflasche", location=living_room, takeable=True, description_german="Vielleicht lässt sich daraus eine Bombe bauen? Man bräuchte nur einen Zünder und einen Timer...")
    alarm_clock = Item(name="alarm_clock", english_name="Alarm Clock", german_name="Wecker", location=leons_room, takeable=True, description_german="Tick Tock Tick Tock")
    candle = Item(name="candle", english_name="Candle", german_name="Kerze", location=fridge, takeable=True, description_german="Für romantische Abende und laute Explosionen!")
    knife = Item(name="knife", english_name="Knife", german_name="Brotmesser", location=kitchen, weapon_ap=10, consume_lp=-100, takeable=True, description_german="Dieses Messer erinnert David an Brot. Hmmm, Brot...")
    bomb = Item(name="bomb", english_name="Bomb", german_name="Bombe", description_german="Ein Angriff hiermit würde viel Schaden anrichten!")
    plant = Item(name="plant", english_name="Plant", german_name="Pflanze", location=davids_room, takeable=True, consume_lp=10)
    monster = Item(name="monster", english_name="Hair Monster", german_name="Haar Monster", location=bathroom, fight_ap=20, fight_lp=140, description_german="Die Haare die Pascals Gäste in der Dusche gelassen haben sind zu einem echten Monster geworden...")
    bed = Item(name="bed", english_name="Bed", german_name="Bett", location=leons_room, fight_ap=0, fight_lp=10, description_german="Das Bett sieht sehr gemuetlich aus.", description_english="The bed looks very comfortable.")
    pfeffi = Item(name="pfeffi", english_name="Pfeffi", german_name="Pfeffi", location=davids_room, consume_lp=5, consume_ap=5, takeable=True)
    b12 = Item(name="b12", english_name="B12", german_name="B12", location=bathroom, takeable=True, consume_lp=20, consume_ap=10, description_german="Besonders für veganer sehr wirkungsvoll!")
    pfeffi2 = Item(name="pfeffi", english_name="Pfeffi", german_name="Pfeffi", location=kitchen, consume_lp=5, consume_ap=5, takeable=True)
    pfeffi3 = Item(name="pfeffi", english_name="Pfeffi", german_name="Pfeffi", location=fridge, consume_lp=5, consume_ap=5, takeable=True)
    paint = Item(name="paint", english_name="Paint", german_name="Farbe", location=davids_room, takeable=True)
    leon = Item(name="leon", english_name="Leon", german_name="Leon", location=leons_room, fight_ap=0, fight_lp=10, description_german=":D :D :D")

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
    db.session.add(leon)
    db.session.commit()

    bomb.ingredients.append(gas_bottle)
    bomb.ingredients.append(candle)
    bomb.ingredients.append(alarm_clock)
    db.session.commit()
    db.session.close()
    print("Database succesfully created.")

set_up()