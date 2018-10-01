from flask import Flask, session, redirect, url_for, escape, request, render_template
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import OperationalError
from david_web.planisphere import db
from david_web import planisphere
from config import secrets # pylint: disable-msg=E0611
from werkzeug.contrib.cache import SimpleCache
import sys
import logging

logging.basicConfig(filename='david_simulator.log' ,level=logging.INFO)
logger = logging.getLogger(__name__)    

if __name__ == "__main__" or "pytest" in sys.modules:
    from david_web import engine
    logger.info('Running Application')

app = Flask(__name__)
logger.info('Connecting to Database')
app.config['SQLALCHEMY_DATABASE_URI'] = secrets.database_uri

db.init_app(app)
db.app = app
logger.info('Database initialized')



cache = SimpleCache()

def cache_image(image_input):
        image = cache.get(image_input)
        if not image:
            image = image_input
            cache.set(image_input, image, timeout=5 * 60)
        return image


@app.route("/", methods=['GET', 'POST'])

def index():
    user_agent = request.headers.get('User-Agent')
    logger.info('User agent: %s', user_agent)
    if 'Android' in user_agent or 'iphone' in user_agent or 'blackberry' in user_agent:
        return render_template("index_mobile.html")
    elif request.method == "GET":
        if session.get('room_name') and session.get('alive'):
            player_data = True
        else:
            player_data = False 
        return render_template("index.html", player_data=player_data)
        
        
    else: 
        new_game = request.form.get('new_game')
        continue_game = request.form.get('continue_game')
        if new_game: #TODO: Add - are you sure? prompt
            session['show_help']=False
            session['room_name'] = planisphere.START
            session['alive'] = True
            session['new_game'] = True
            session['data_dict'] = {'message' : False,
            'image' : 'static/images/davids_room.jpg',
            'room_name': 'davids_room',
                'character' : {
                    'Health': 100,
                    'Attack_Points': 20,
                    'States' : [],
                    'Inventory' : {}
                    },
                'opponents' : {},
                'taken_items' : [],
                'room_log' : ['davids_room']
        }
            return redirect(url_for("game"))
        elif continue_game:
            session['show_help']=False
            return redirect(url_for("game"))
        else:
            #TODO: Add Error
            return render_template("error.html")
        
    



@app.route("/game", methods=['GET', 'POST'])
def game():
    logging.debug('Initializing game page')
    new_game = session.get('new_game')
    data_dict = session.get('data_dict')
    image = cache_image(data_dict.get('image'))
    message = data_dict.get('message')
    room_name = data_dict.get('room_name')
    david_lp = data_dict.get('character').get('Health')
    show_help = session.get('show_help')
    logging.debug('data_dict: %s', data_dict)

    if request.method == "GET":
        logging.debug('GET method /game')
        if david_lp <= 0:
            session['alive'] = False
            return render_template("you_died.html")

        if room_name:
            logging.debug('Loading Room')
            room = engine.match_room(room_name)
            logging.debug('Room assigned: %s', room)
            return render_template("show_room.html", room=room, message=message, image=image, new_game=new_game, show_help=show_help)
        else:
            session['alive'] = False
            return render_template("error.html")

    else:
        tutorial = request.form.get('tutorial_off')
        help_request = request.form.get('help_request')
        help_off = request.form.get('help_off')
        action = request.form.get('action')

        if tutorial:
            session['new_game']=False
        if help_request:
            session['new_game']=False
            session['show_help']=True
        if help_off:
            session['show_help']=False
        if room_name and action:
            session['new_game']=False
            room = engine.match_room(room_name)

            action_instance = engine.Action(room, action, data_dict)
            data_dict = action_instance.determine_action()

            session['data_dict'] = data_dict
        return redirect(url_for("game"))

@app.route("/about", methods=['GET', 'POST'])
def about():
    return render_template('about.html')

@app.route("/credits", methods=['GET', 'POST'])
def credits():
    return render_template('credits.html')

app.secret_key = secrets.secret_app_key

if __name__ == "__main__":
    app.run(host='0.0.0.0')
