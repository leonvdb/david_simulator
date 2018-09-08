from david_web import gamestate
attack = {'bed': {'message': f"""Das Bett ist sehr gemuetlich!""", 'special_action': True}}


def special_attack(self):
    if self.objects[0] == 'bed':
        gamestate.states.append('müde')
