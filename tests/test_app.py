from app import app
from contextlib import contextmanager
from flask import appcontext_pushed, g

import pytest

@pytest.fixture(scope='session')
def client():

    app.config['TESTING'] = True
    client = app.test_client()

    yield client

# @pytest.contextmanager
# def location_set(app, location):



def test_index(client):
    rv = client.get('/', follow_redirects=True)
    assert rv.status_code == 200


def test_game(client):

    rv = client.get('/game', follow_redirects=True)
    assert rv.status_code, 200
    print(">>>> client.get(room_name)", client.get('room_name'))
    assert b"Davids Room" in rv.data

    data = {'action': 'in den flur'}
    rv = client.post('/game', follow_redirects=True, data=data)
    assert rv.status_code == 200
    assert b"Hallway" in rv.data

    data = {'action': 'selbstmord'}
    rv = client.post('/game', follow_redirects=True, data=data)
    assert rv.status_code == 200
    assert b"Death" in rv.data

# def test_back_home(client):
#
#     with location_set(app, 'davids_room')
#         rv = client.get('/game', follow_redirects=True)
#         assert rv.status_code, 200
#         print(">>>> rv.data", rv.data)
#         assert b"Davids Room" in rv.data
