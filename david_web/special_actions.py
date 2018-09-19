attack = {'bed': {'message': f"""Das Bett ist sehr gemuetlich!""", 'image': False},
          'leon' : {'message' : False, 'image': '/static/images/kill_leon.jpg'}}

def special_actions(action,data_dict):
    if action.action_type == 'attack':
        if action.objects[0] == 'bed':
            data_dict['message'] = data_dict.get('message') + F"""Das bett war sehr gemuetlich. David erhät Status \"müde\"."""
            data_dict['character']['States'].append('muede')
        elif action.objects[0] == 'leon' and data_dict['opponents']['leon']['lp']<=0:
            data_dict['image'] = '/static/images/kill_leon.jpg'
    elif action.action_type == 'go':
        if data_dict['room_name'] == 'leons_room' and 'leon' in list(data_dict['opponents'].keys()):
            if data_dict['opponents']['leon']['lp']<=0:
                data_dict['image'] = '/static/images/leons_room_dead.jpg'
    return data_dict