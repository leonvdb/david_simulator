from david_web import lexicon

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
                         'paths': ['hallway'],
                         'objects': []},
         'bathroom':    {'name': 'Bathroom',
                         'description': 'Description of Bathroom',
                         'paths': ['hallway'],
                         'objects': ['monster', 'b12', 'toilette']},

         }
