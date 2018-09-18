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
            session['final_action'] = False
            session['data_dict'] = {'final_action' : False,
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
    action_name = session.get('final_action')
    room_name = session.get('room_name')
    data_dict = session.get('data_dict')
    david_lp = data_dict.get('character').get('Health')

    if request.method == "GET":

        if david_lp <= 0:
            session['alive'] = False
            return render_template("you_died.html")

        if room_name:
            room = engine.match_room(room_name)
            return render_template("show_room.html", room=room, action_name=action_name)
        else:
            #TODO: Add Error
            return render_template("you_died.html")

    else:
        action = request.form.get('action')

        if room_name and action:
            room = engine.match_room(room_name)

            action_instance = engine.Action(room, action, data_dict)
            final_action = action_instance.determine_action()

            if action_instance.action_type != 'go':

                session['room_name'] = engine.name_room(room)
                session['final_action'] = final_action.get('final_action')
                session['data_dict'] = final_action
            else:

                session['room_name'] = final_action.get('final_action')
                session['data_dict'] = final_action
                session['final_action'] = False

        return redirect(url_for("game"))


app.secret_key = secrets.secret_app_key

if __name__ == "__main__":
    app.run(debug=True)
