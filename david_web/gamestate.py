from david_web import planisphere
from flask import Flask, session
from flask_sqlalchemy import SQLAlchemy
from config import secrets # pylint: disable-msg=E0611
from david_web.planisphere import db

character_stats = {
    'Health': 100,
    'Attack_Points': 20
}

inventory = {}
taken_items = []

states = []

opponents = {}

room_log = ['davids_room']
