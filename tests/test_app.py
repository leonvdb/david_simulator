from app import app
from david_web import engine

import pytest


@pytest.fixture(scope='session')
def client():

    app.config['TESTING'] = True
    client = app.test_client()

    yield client


@pytest.fixture()
def new_client():

    app.config['TESTING'] = True
    client = app.test_client()

    yield client


@pytest.fixture()
def new_client2():

    app.config['TESTING'] = True
    client = app.test_client()

    yield client


def test_index(client):
    rv = client.get('/', follow_redirects=True)
    assert rv.status_code == 200


def test_game(client):

    rv = client.get('/', follow_redirects=True)
    assert rv.status_code == 200
    data = {'new_game': True}
    rv = client.post('/', follow_redirects=True, data=data)
    assert b"Davids Room" in rv.data

    data = {'action': 'geh zurück'}
    rv = client.post('/game', follow_redirects=True, data=data)
    assert rv.status_code == 200
    assert b'nirgendwo' in rv.data

    data = {'action': 'geh in den flur'}
    rv = client.post('/game', follow_redirects=True, data=data)
    assert rv.status_code == 200
    assert b"Hallway" in rv.data


def test_back_home(new_client):

    rv = new_client.get('/', follow_redirects=True)
    assert rv.status_code == 200
    data = {'new_game': True}
    rv = new_client.post('/', follow_redirects=True, data=data)
    assert b"Davids Room" in rv.data

    data = {'action': 'greif die pflanze an'}
    rv = new_client.post('/game', follow_redirects=True, data=data)
    assert rv.status_code == 200
    assert b'kannst du nicht' in rv.data

    data = {'action': 'geh in den flur'}
    rv = new_client.post('/game', follow_redirects=True, data=data)
    assert rv.status_code == 200
    assert b"Hallway" in rv.data

    data = {'action': 'geh in die Küche'}
    rv = new_client.post('/game', follow_redirects=True, data=data)
    assert rv.status_code == 200
    assert b"Kitchen" in rv.data

    data = {'action': 'nimm das Messer'}
    rv = new_client.post('/game', follow_redirects=True, data=data)
    assert rv.status_code == 200
    assert b"wurde deinem Inventar" in rv.data

    data = {'action': 'öffne den Kühlschrank'}
    rv = new_client.post('/game', follow_redirects=True, data=data)
    assert rv.status_code == 200
    assert b"Fridge" in rv.data

    data = {'action': 'nimm die Kerze'}
    rv = new_client.post('/game', follow_redirects=True, data=data)
    assert rv.status_code == 200
    assert b"wurde deinem Inventar" in rv.data

    data = {'action': 'gamestate'}
    rv = new_client.post('/game', follow_redirects=True, data=data)
    assert rv.status_code == 200
    assert b"Knife" in rv.data

    data = {'action': 'greif mit dem Messer etwas an'}
    rv = new_client.post('/game', follow_redirects=True, data=data)
    assert rv.status_code == 200
    assert b'in folgender Form' in rv.data
    assert b'Messer' in rv.data

    data = {'action': 'geh in den Flur'}
    rv = new_client.post('/game', follow_redirects=True, data=data)
    assert rv.status_code == 200

    data = {'action': 'geh in Davids Zimmer'}
    rv = new_client.post('/game', follow_redirects=True, data=data)
    assert rv.status_code == 200
    assert b"Davids Room" in rv.data

    data = {'action': 'greif das bett mit dem Messer an'}
    rv = new_client.post('/game', follow_redirects=True, data=data)
    assert rv.status_code == 200
    assert b'besiegt' in rv.data
    assert b'gemuetlich' in rv.data
    assert b'30' in rv.data
    assert b'Bett' in rv.data

    data = {'action': 'greif das bett an'}
    rv = new_client.post('/game', follow_redirects=True, data=data)
    assert rv.status_code == 200
    assert b'besiegt' in rv.data

    data = {'action': 'greif das bett an'}
    rv = new_client.post('/game', follow_redirects=True, data=data)
    assert rv.status_code == 200
    assert b'nicht nochmal' in rv.data

    data = {'action': 'nimm den salat'}
    rv = new_client.post('/game', follow_redirects=True, data=data)
    assert rv.status_code == 200

    data = {'action': 'iss das bett auf'}
    rv = new_client.post('/game', follow_redirects=True, data=data)
    assert rv.status_code == 200
    assert b'kannst du nicht konsumieren' in rv.data

    data = {'action': 'bau eine bombe'}
    rv = new_client.post('/game', follow_redirects=True, data=data)
    assert rv.status_code == 200
    assert b'fehlen noch folgende Objekte' in rv.data

    data = {'action': 'geh in den Flur'}
    rv = new_client.post('/game', follow_redirects=True, data=data)
    assert rv.status_code == 200
    assert b"Hallway" in rv.data

    data = {'action': 'geh in das Wohnzimmer'}
    rv = new_client.post('/game', follow_redirects=True, data=data)
    assert rv.status_code == 200
    assert b"Living Room" in rv.data

    data = {'action': 'nimm die Gasflasche'}
    rv = new_client.post('/game', follow_redirects=True, data=data)
    assert rv.status_code == 200
    assert b"wurde deinem Inventar" in rv.data

    data = {'action': 'geh in den Flur'}
    rv = new_client.post('/game', follow_redirects=True, data=data)
    assert rv.status_code == 200
    assert b"Hallway" in rv.data

    data = {'action': 'geh in Leons Zimmer'}
    rv = new_client.post('/game', follow_redirects=True, data=data)
    assert rv.status_code == 200
    assert b"Leons Room" in rv.data

    data = {'action': 'nimm den Wecker'}
    rv = new_client.post('/game', follow_redirects=True, data=data)
    assert rv.status_code == 200
    assert b"wurde deinem Inventar" in rv.data

    data = {'action': 'bau eine Bombe'}
    rv = new_client.post('/game', follow_redirects=True, data=data)
    assert rv.status_code == 200
    assert b'erfolgreich' in rv.data

    data = {'action': 'gamestate'}
    rv = new_client.post('/game', follow_redirects=True, data=data)
    assert rv.status_code == 200
    assert b"Candle" not in rv.data
    assert b"Bomb" in rv.data

    data = {'action': 'bau eine Kerze'}
    rv = new_client.post('/game', follow_redirects=True, data=data)
    assert rv.status_code == 200
    assert b'kannst du nicht bauen'

    data = {'action': 'geh in den flur'}
    rv = new_client.post('/game', follow_redirects=True, data=data)
    assert rv.status_code == 200
    assert b"Hallway" in rv.data

    data = {'action': 'iss das messer auf'}
    rv = new_client.post('/game', follow_redirects=True, data=data)
    assert rv.status_code == 200
    assert b'kannst du nicht' in rv.data

    data = {'action': 'greif das monster an'}
    rv = new_client.post('/game', follow_redirects=True, data=data)
    assert rv.status_code == 200
    assert b'in diesem Raum'in rv.data

    data = {'action': 'geh in das badezimmer'}
    rv = new_client.post('/game', follow_redirects=True, data=data)
    assert rv.status_code == 200
    assert b"Bathroom" in rv.data

    data = {'action': 'iss das B12'}
    rv = new_client.post('/game', follow_redirects=True, data=data)
    assert rv.status_code == 200

    data = {'action': 'greif das monster an'}
    rv = new_client.post('/game', follow_redirects=True, data=data)
    assert rv.status_code == 200
    assert b'David hat noch 100' in rv.data

    data = {'action': 'geh in den flur'}
    rv = new_client.post('/game', follow_redirects=True, data=data)
    assert rv.status_code == 200
    assert b"Hallway" in rv.data

    data = {'action': 'geh in davids zimmer'}
    rv = new_client.post('/game', follow_redirects=True, data=data)
    assert rv.status_code == 200
    assert b"Davids Room" in rv.data

    data = {'action': 'iss die pflanze auf'}
    rv = new_client.post('/game', follow_redirects=True, data=data)
    assert rv.status_code == 200

    data = {'action': 'geh in den flur'}
    rv = new_client.post('/game', follow_redirects=True, data=data)
    assert rv.status_code == 200
    assert b'Hallway' in rv.data

    data = {'action': 'geh in die Küche'}
    rv = new_client.post('/game', follow_redirects=True, data=data)
    assert rv.status_code == 200
    assert b'Kitchen' in rv.data

    data = {'action': 'trink den pfeffi'}
    rv = new_client.post('/game', follow_redirects=True, data=data)
    assert rv.status_code == 200
    assert b'konsumiert' in rv.data

    data = {'action': 'öffne den Kühlschrank'}
    rv = new_client.post('/game', follow_redirects=True, data=data)
    assert rv.status_code == 200
    assert b'Fridge' in rv.data

    data = {'action': 'nimm den pfeffi'}
    rv = new_client.post('/game', follow_redirects=True, data=data)
    assert rv.status_code == 200

    data = {'action': 'trink den pfeffi'}
    rv = new_client.post('/game', follow_redirects=True, data=data)
    assert rv.status_code == 200
    assert b'konsumiert' in rv.data

    data = {'action': 'geh zurück'}
    rv = new_client.post('/game', follow_redirects=True, data=data)
    assert rv.status_code == 200
    assert b'Kitchen' in rv.data



def test_errors(new_client):

    rv = new_client.get('/', follow_redirects=True)
    assert rv.status_code == 200
    data = {'new_game': True}
    rv = new_client.post('/', follow_redirects=True, data=data)
    assert b"Davids Room" in rv.data

    data = {'action': 'geh geh geh!'}
    rv = new_client.post('/game', follow_redirects=True, data=data)
    assert rv.status_code == 200
    assert b"zu viele Verben" in rv.data

    data = {'action': 'Flur!'}
    rv = new_client.post('/game', follow_redirects=True, data=data)
    assert rv.status_code == 200
    assert b"kein bekanntes Verb" in rv.data

    data = {'action': 'geh weg!'}
    rv = new_client.post('/game', follow_redirects=True, data=data)
    assert rv.status_code == 200
    assert b"keine bekannte Richtung" in rv.data
