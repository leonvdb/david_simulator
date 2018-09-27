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
    assert b"Davids Zimmer" in rv.data

    data = {'action': 'geh zurück'}
    rv = client.post('/game', follow_redirects=True, data=data)
    assert rv.status_code == 200
    assert b'nirgendwo' in rv.data

    data = {'action': 'wohin'}
    rv = client.post('/game', follow_redirects=True, data=data)
    assert rv.status_code == 200
    assert b'Flur' in rv.data

    data = {'action': 'welche'}
    rv = client.post('/game', follow_redirects=True, data=data)
    assert rv.status_code == 200
    assert b'Farbe' in rv.data

    data = {'action': 'guck die farbe an und den sessel an.'}
    rv = client.post('/game', follow_redirects=True, data=data)
    assert rv.status_code == 200
    assert b'zu viele' in rv.data

    data = {'action': 'guck die Sahne.'}
    rv = client.post('/game', follow_redirects=True, data=data)
    assert rv.status_code == 200
    assert b'kein' in rv.data

    data = {'action': 'guck die Kerze.'}
    rv = client.post('/game', follow_redirects=True, data=data)
    assert rv.status_code == 200
    assert b'weder' in rv.data

    data = {'action': 'guck die pflanze an.'}
    rv = client.post('/game', follow_redirects=True, data=data)
    assert rv.status_code == 200
    assert b'Merkmale' in rv.data


    data = {'action': 'geh in den flur'}
    rv = client.post('/game', follow_redirects=True, data=data)
    assert rv.status_code == 200
    assert b"Flur" in rv.data


def test_back_home(new_client):

    rv = new_client.get('/', follow_redirects=True)
    assert rv.status_code == 200
    data = {'new_game': True}
    rv = new_client.post('/', follow_redirects=True, data=data)
    assert b"Davids Zimmer" in rv.data

    data = {'action': 'greif die pflanze an'}
    rv = new_client.post('/game', follow_redirects=True, data=data)
    assert rv.status_code == 200
    assert b'kannst du nicht' in rv.data

    data = {'action': 'geh in den flur'}
    rv = new_client.post('/game', follow_redirects=True, data=data)
    assert rv.status_code == 200
    assert b"Flur" in rv.data

    data = {'action': 'geh in die Küche'}
    rv = new_client.post('/game', follow_redirects=True, data=data)
    assert rv.status_code == 200


    data = {'action': 'nimm das Messer'}
    rv = new_client.post('/game', follow_redirects=True, data=data)
    assert rv.status_code == 200
    assert b"wurde deinem Inventar" in rv.data

    data = {'action': 'what'}
    rv = new_client.post('/game', follow_redirects=True, data=data)
    assert rv.status_code == 200
    assert b"Pfeffi" in rv.data
    assert b"Brotmesser" not in rv.data

    data = {'action': 'öffne den Kühlschrank'}
    rv = new_client.post('/game', follow_redirects=True, data=data)
    assert rv.status_code == 200

    data = {'action': 'nimm die Kerze'}
    rv = new_client.post('/game', follow_redirects=True, data=data)
    assert rv.status_code == 200
    assert b"wurde deinem Inventar" in rv.data

    data = {'action': 'geh zurück'}
    rv = new_client.post('/game', follow_redirects=True, data=data)
    assert rv.status_code == 200

    data = {'action': 'gamestate'}
    rv = new_client.post('/game', follow_redirects=True, data=data)
    assert rv.status_code == 200
    assert b"Brotmesser" in rv.data

    data = {'action': 'greif mit dem Messer etwas an'}
    rv = new_client.post('/game', follow_redirects=True, data=data)
    assert rv.status_code == 200
    assert b'in folgender Form' in rv.data
    assert b'Messer' in rv.data

    data = {'action': 'geh in den Flur'}
    rv = new_client.post('/game', follow_redirects=True, data=data)
    assert rv.status_code == 200

    data = {'action': 'geh in Leons Zimmer'}
    rv = new_client.post('/game', follow_redirects=True, data=data)
    assert rv.status_code == 200
    assert b"Leons Zimmer" in rv.data

    data = {'action': 'guck das bett an.'}
    rv = new_client.post('/game', follow_redirects=True, data=data)
    assert rv.status_code == 200
    assert b'gemuetlich' in rv.data

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

    data = {'action': 'gamestate'}
    rv = new_client.post('/game', follow_redirects=True, data=data)
    assert rv.status_code == 200
    assert b"muede" in rv.data

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
    assert b"Flur" in rv.data

    data = {'action': 'geh in das Wohnzimmer'}
    rv = new_client.post('/game', follow_redirects=True, data=data)
    assert rv.status_code == 200
    assert b"Wohnzimmer" in rv.data

    data = {'action': 'nimm die Gasflasche'}
    rv = new_client.post('/game', follow_redirects=True, data=data)
    assert rv.status_code == 200
    assert b"wurde deinem Inventar" in rv.data

    data = {'action': 'geh in den Flur'}
    rv = new_client.post('/game', follow_redirects=True, data=data)
    assert rv.status_code == 200
    assert b"Flur" in rv.data

    data = {'action': 'geh in Leons Zimmer'}
    rv = new_client.post('/game', follow_redirects=True, data=data)
    assert rv.status_code == 200
    assert b"Leons Zimmer" in rv.data

    data = {'action': 'greif Leon an'}
    rv = new_client.post('/game', follow_redirects=True, data=data)
    assert rv.status_code == 200
    assert b"Leons Zimmer" in rv.data
    assert b"besiegt" in rv.data

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
    assert b"Flur" in rv.data

    data = {'action': 'iss die bombe auf'}
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
    assert b"Badezimmer" in rv.data

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
    assert b"Flur" in rv.data

    data = {'action': 'geh in davids zimmer'}
    rv = new_client.post('/game', follow_redirects=True, data=data)
    assert rv.status_code == 200
    assert b"Davids Zimmer" in rv.data

    data = {'action': 'iss die pflanze auf'}
    rv = new_client.post('/game', follow_redirects=True, data=data)
    assert rv.status_code == 200

    data = {'action': 'geh in den flur'}
    rv = new_client.post('/game', follow_redirects=True, data=data)
    assert rv.status_code == 200
    assert b'Flur' in rv.data

    data = {'action': 'geh in die Küche'}
    rv = new_client.post('/game', follow_redirects=True, data=data)
    assert rv.status_code == 200


    data = {'action': 'trink den pfeffi'}
    rv = new_client.post('/game', follow_redirects=True, data=data)
    assert rv.status_code == 200
    assert b'konsumiert' in rv.data

    data = {'action': 'öffne den Kühlschrank'}
    rv = new_client.post('/game', follow_redirects=True, data=data)
    assert rv.status_code == 200

    data = {'action': 'nimm den pfeffi'}
    rv = new_client.post('/game', follow_redirects=True, data=data)
    assert rv.status_code == 200

    data = {'action': 'trink den pfeffi'}
    rv = new_client.post('/game', follow_redirects=True, data=data)
    assert rv.status_code == 200
    assert b'konsumiert' in rv.data
    assert b'Superdrunk' in rv.data

    data = {'action': 'geh zurück'}
    rv = new_client.post('/game', follow_redirects=True, data=data)
    assert rv.status_code == 200




def test_errors(new_client):

    rv = new_client.get('/', follow_redirects=True)
    assert rv.status_code == 200
    data = {'new_game': True}
    rv = new_client.post('/', follow_redirects=True, data=data)
    assert b"Davids Zimmer" in rv.data

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
