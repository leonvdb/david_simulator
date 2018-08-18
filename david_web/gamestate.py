from david_web import planisphere
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import secrets # pylint: disable-msg=E0611
from david_web.planisphere import db

character_stats = {
    'Health': 100,
    'Attack_Points': 20
}


states = []

opponents = {'monster': {'ap': 20, 'lp': 140},
             'bed': {'ap': 0, 'lp': 10}}

room_log = ['davids_room']
