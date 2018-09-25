attack = {'bed': {'message': f"""Das Bett ist sehr gemuetlich!""", 'image': False},
          'leon' : {'message' : False, 'image': '/static/images/kill_leon.jpg'}}

def special_actions(action,data_dict):
    if action.action_type == 'attack':
        if action.objects[0] == 'bed':
            data_dict['message'] = data_dict.get('message') + F"""Das bett war sehr gemuetlich."""
            data_dict = append_state('muede', data_dict)
        elif action.objects[0] == 'leon' and data_dict['opponents']['leon']['lp']<=0:
            data_dict['image'] = '/static/images/kill_leon.jpg'
    elif action.action_type == 'go':
        if data_dict['room_name'] == 'leons_room' and 'leon' in list(data_dict['opponents'].keys()):
            if data_dict['opponents']['leon']['lp']<=0:
                data_dict['image'] = '/static/images/leons_room_dead.jpg'
    elif action.action_type == 'consume':
        if action.objects[0] == 'plant':
            data_dict = append_state('Vegan', data_dict)
        elif action.objects[0] == 'pfeffi' and 'Drunk' not in  data_dict['character']['States']:
            data_dict = append_state('Drunk', data_dict)
        elif action.objects[0] == 'pfeffi' and 'Drunk' in  data_dict['character']['States']:
            data_dict = append_state('Superdrunk', data_dict, 'Drunk')
        elif action.objects[0] == 'pfeffi' and 'Superdrunk' in  data_dict['character']['States']:
            data_dict = append_state('Crazydrunk', data_dict, 'Superdrunk')
    elif action.action_type == 'use':
        if action.objects[0] == 'chair':
            data_dict['image'] = '/static/images/on_the_phone.jpg'
            data_dict['message'] = "David macht es sich auf dem Sessel gemütlich und checkt Instagram"
    return data_dict

def append_state(state_name, data_dict, remove_me=None):
    if remove_me:
        data_dict['character']['States'].remove(remove_me)
    data_dict['character']['States'].append(state_name)
    data_dict['message'] = data_dict.get('message') + f"""
                David erhät neuen Status \"{state_name}\".
                """
    return data_dict