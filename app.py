from flask import Flask, session, redirect, url_for, escape, request, render_template
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import OperationalError
from david_web.planisphere import db
from david_web import planisphere
from config import secrets # pylint: disable-msg=E0611
import sys

if __name__ == "__main__" or "pytest" in sys.modules:
    from david_web import engine

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = secrets.database_uri

db.init_app(app)
db.app = app



@app.route("/", methods=['GET', 'POST'])
def index():
    if request.method == "GET":
        if session.get('room_name') and session.get('alive'):
            player_data = True
        else:
            player_data = False 
        return render_template("index.html", player_data=player_data)
        
        
    else: 
        new_game = request.form.get('new_game')
        continue_game = request.form.get('continue_game')
        if new_game: #TODO: Add - are you sure? prompt
            session['room_name'] = planisphere.START
            session['alive'] = True
            session['data_dict'] = {'message' : False,
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
            return redirect(url_for("game"))
        else:
            #TODO: Add Error
            return render_template("error.html")
        
    



@app.route("/game", methods=['GET', 'POST'])
def game():
    session['character_stats'] = {
    'Health': 100,
    'Attack_Points': 20
}
    
    data_dict = session.get('data_dict')
    message = data_dict.get('message')
    room_name = data_dict.get('room_name') 
    david_lp = data_dict.get('character').get('Health')

    if request.method == "GET":

        if david_lp <= 0:
            session['alive'] = False
            return render_template("you_died.html")

        if room_name:
            room = engine.match_room(room_name)
            return render_template("show_room.html", room=room, message=message)
        else:
            session['alive'] = False
            return render_template("error.html")

    else:
        action = request.form.get('action')

        if room_name and action:
            room = engine.match_room(room_name)

            action_instance = engine.Action(room, action, data_dict)
            data_dict = action_instance.determine_action()

            session['data_dict'] = data_dict

        return redirect(url_for("game"))


app.secret_key = secrets.secret_app_key

if __name__ == "__main__":
    app.run(debug=True)
