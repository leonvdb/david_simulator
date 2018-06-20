from david_web.engine import *
attack = {'bett': {'message': f"""Das Bett ist sehr gemuetlich!""", 'special_action': True}}


def special_attack(self):
    if self.objects[0] == 'bett':
        gamestate.states.append('müde')
