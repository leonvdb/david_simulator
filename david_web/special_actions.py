from david_web import planisphere
attack = {'bed': {'message': f"""Das Bett ist sehr gemuetlich!""", 'image': False},
          'leon' : {'message' : False, 'image': '/static/images/kill_leon.jpg'}}

def special_actions(action,data_dict):
    if action.action_type == 'attack':
        if action.objects[0] == 'bed':
            data_dict['message'] = data_dict.get('message') + F"""Das bett war sehr gemuetlich."""
            data_dict = append_state('muede', data_dict)
        elif action.objects[0] == 'leon' and data_dict['opponents']['leon']['lp']<=0:
            data_dict['image'] = '/static/images/kill_leon.jpg'
        elif action.objects[0] == 'ratking' and not data_dict['image'] == '/static/images/trash.jpg':
            data_dict['character']['Health'] += 1000
            data_dict['opponents']['ratking']['lp'] = 20000
            return action.error('no opponents')
        if action.with_action == True:
            if action.objects[1] == 'bomb':
                del data_dict['character']['Inventory']['bomb']
    elif action.action_type == 'go':
        if data_dict['room_name'] == 'leons_room' and 'leon' in list(data_dict['opponents'].keys()):
            if data_dict['opponents']['leon']['lp']<=0:
                data_dict['image'] = '/static/images/leons_room_dead.jpg'
        if data_dict['room_name'] == 'spaeti':
            if 'Drunk' in data_dict['character']['States']:
                data_dict = steal('spezi', data_dict)
            elif 'Superdrunk' in data_dict['character']['States']:
                data_dict = steal('ravioli', data_dict)
            elif 'Crazydrunk' in data_dict['character']['States']:
                data_dict = steal('marzipan', data_dict)
            elif 'Ultradrunk' in data_dict['character']['States']:
                data_dict = steal('superpfeffi', data_dict)   
    elif action.action_type == 'consume':
        if action.objects[0] == 'plant':
            data_dict = append_state('Vegan', data_dict)
        elif action.objects[0] == 'pfeffi' and 'Drunk' not in  data_dict['character']['States'] and not any('drunk'in s for s in data_dict['character']['States']):
            data_dict = append_state('Drunk', data_dict)
        elif action.objects[0] == 'pfeffi' and 'Drunk' in  data_dict['character']['States']:
            data_dict = append_state('Superdrunk', data_dict, 'Drunk')
        elif action.objects[0] == 'pfeffi' and 'Superdrunk' in  data_dict['character']['States']:
            data_dict = append_state('Crazydrunk', data_dict, 'Superdrunk')
        elif action.objects[0] == 'pfeffi' and 'Crazydrunk' in  data_dict['character']['States']:
            data_dict = append_state('Ultradrunk', data_dict, 'Crazydrunk')
        elif action.objects[0] == 'superpfeffi':
            data_dict = append_state('Drunkception', data_dict, 'Ultradrunk')
        elif action.objects[0] == 'b12' and 'Vegan' in data_dict['character']['States']:
            data_dict['character']['Attack_Points'] += 10
            data_dict['character']['Health'] += 30
            data_dict['message'] = """David konsumiert B12. Als veganer hat es bei David besondere Wirkung!
            David bekommt 20 Angriffspunkte von B12. David bekommt 50 Lebenspunkte von B12."""
    elif action.action_type == 'build':
        if action.objects[0] == 'bomb':
            data_dict['image'] = '/static/images/bomb.jpg'
    elif action.action_type == 'use':
        if action.objects[0] == 'toilet':
            data_dict['message'] = "David setzt sich auf die Toilette und liest."
            data_dict['image'] = '/static/images/on_the_toilet.jpg'
            if 'Techno Viking' in data_dict['character']['States']:
                data_dict['message'] = "David macht einen riesigen Techno Viking Haufen. Leon verliert 50 Lebenspunkte."
                if 'leon' not in data_dict['opponents'].keys():
                    data_dict['opponents']['leon'] = {'ap': 99, 'lp': 4950}
                else:
                    data_dict['opponents']['leon']['lp'] -= 50
        elif action.objects[0] == 'paint' and 'bike' in list(data_dict['character']['Inventory'].keys()):
            data_dict['message'] = "David malt das Fahrrad an. Schön!"
        elif action.objects[0] == 'chair':
            data_dict['image'] = '/static/images/on_the_phone.jpg'
            data_dict['message'] = "David macht es sich auf dem Sessel gemütlich und checkt Instagram"
        elif action.objects[0] == 'vinyl':
            data_dict['message'] = "David macht Musik an."
            data_dict = append_state('Techno Viking', data_dict)
        elif action.objects[0] == 'window_key' and data_dict['room_name'] == 'kitchen':
            query_item = planisphere.Item.query.filter_by(name='joseph').first()
            if query_item.id not in data_dict['taken_items']:
                data_dict['character']['Inventory'][query_item.name] = 1
                data_dict['taken_items'].append(query_item.id)
                data_dict['message'] = F"""Du benutzt den Schlüssel um das Fenster zu öffnen und Findest auf der äusseren Fensterbank Joseph, den mitlerweile flachen
                Halloweenkürbis von letztem Jahr. Joseph wurde deinem Inventar hinzugefügt."""
            else:
                data_dict['message'] = F"""Du machst das Fenster auf, aber hier befindet sich nichts mehr."""
        elif action.objects[0] == 'joseph' and 'Drunkception' in data_dict['character']['States']:
            data_dict['message'] = F"""In diesem Zustand von Trunkenheit überkommt es David und er zieht sich Joseph über den Kopf.
            Ihm wird sehr schwindelig und verliert das Bewusstsein... Als David wieder aufwacht ist er nicht mehr er selbst. Er ist mit 
            Joseph verschmolzen und hat so Superkräft bekommen. David erhält 9000 Angriffspunkte und 2900 Lebenspunkte."""
            data_dict['character']['Health'] += 2900
            data_dict['character']['Attack_Points'] += 9000
            append_state('Superjoseph', data_dict, 'Drunkception')
        elif action.objects[0] == 'trash' and 'bin' not in list(data_dict['character']['Inventory'].keys()):
            data_dict['message'] = F"""Das würdest du wirklich nicht benutzen es sei denn du möchtest Müll loswerden."""
        elif action.objects[0] == 'trash' and 'bin' in list(data_dict['character']['Inventory'].keys()):
            data_dict['image'] = '/static/images/trash.jpg'
            data_dict['message'] = F"""Du öffnest die Tonne um den Müllsack reinzuwerfen. Irgendetwas raschelt sehr laut unter dem Koymüll."""
            del data_dict['character']['Inventory']['bin']
    elif action.action_type == 'inspect':
        if action.objects[0] == 'monster' and 'monster' in list(data_dict['opponents'].keys()):
            if data_dict['opponents']['monster']['lp']<=0:
                data_dict['message'] = F"""Du untersuchst die Monsterleiche genauer und findest eine Notitz:
                \" Masterplan um auf ewig gemütlich in der Wanne zu liegen: 1. Bombe aus Gasflasche, Kerze und Wecker bauen.
                2. Mit Bombe Leon in die Luft sprengen damit er das Bad nichtmehr benutzt. 3. Den Legendären Superpfeffi aus dem Späti bekommen.
                4. David mit Superpfeffi abfüllen damit auch er für immer ausgeschaltet ist.\" """
        elif action.objects[0] == 'leon' and 'leon' in list(data_dict['opponents'].keys()):
            if data_dict['opponents']['leon']['lp']<=0:
                query_item = planisphere.Item.query.filter_by(name='window_key').first()
                if query_item.id not in data_dict['taken_items']:
                    data_dict['character']['Inventory'][query_item.name] = 1
                    data_dict['taken_items'].append(query_item.id)
                    data_dict['message'] = F"""Du untersuchst Leons Leiche genauer und findest einen Schlüssel. Der Schlüssel wurde deinem Inventar hinzugefügt."""
        elif action.objects[0] == 'picture':
            data_dict['image'] = '/static/images/picture.jpg'
        elif action.objects[0] == 'wall':
            data_dict['image'] = '/static/images/wall.jpg'
        elif action.objects[0] == 'mailboxes' and 'mailboxes' in list(data_dict['opponents'].keys()):
            if data_dict['opponents']['mailboxes']['lp']<=0:
                data_dict['message'] = """David öffnet eine der Türen und findet einen Brief der Vigor Hausverwaltung: 
                Im Innenhof haben wir mit schweren Problemen zu kämpfen. Insbesondere mit dem Rattenkönig der eine Angriffstärke von 
                1000 und Leben von 20000 hat. Er ist auch sehr schwer zu finden - Wenn man den gelben Müllcontainer öffnet ist 
                er zwar immernoch nicht zu sehen, aber man kann ihn angreifen! Wer auch immer ihn erlegt dem gebürt hohes lob! 
                Wenn er erlegt wurde wird nach einem Wort gefragt werden. Das Wort lautet: Bundeskegelbahn."""
    elif action.action_type == 'what':
        if data_dict['room_name'] == 'yard':
            data_dict['message'] = data_dict.get('message').replace(", Rattenkönig", "")

    return data_dict

def append_state(state_name, data_dict, remove_me=None):
    if remove_me:
        data_dict['character']['States'].remove(remove_me)
    if state_name not in data_dict['character']['States']:
        data_dict['character']['States'].append(state_name)
        data_dict['message'] = data_dict.get('message') + f"""
                David erhät neuen Status \"{state_name}\".
                """
    elif state_name in data_dict['character']['States']:
        data_dict['message'] = data_dict.get('message') + f"""
                David ist bereits \"{state_name}\".
                """
    return data_dict

def steal(item_name, data_dict):
    query_item = planisphere.Item.query.filter_by(name=item_name).first()
    if query_item.id not in data_dict['taken_items']:
        data_dict['character']['Inventory'][query_item.name] = 1
        data_dict['taken_items'].append(query_item.id)
        data_dict['message'] =  f"""Du betrittst den Späti.
                David ist einem Zustand von Trunkenheit, dass er einfach das Objekt  \"{query_item.german_name}\" klaut!
                Es wurde deinem Inventar hinzugefügt.
                """

    return data_dict