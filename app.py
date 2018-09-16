from flask import Flask, session, redirect, url_for, escape, request, render_template
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import OperationalError
from david_web.planisphere import db
from david_web import engine
from david_web import gamestate
from david_web import planisphere
import create_db
from config import secrets # pylint: disable-msg=E0611

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = secrets.database_uri

db.init_app(app)
db.app = app



@app.route("/")
def index():
    session['room_name'] = planisphere.START
    session['final_action'] = False

    return render_template("index.html")
    # return redirect(url_for("game"))


@app.route("/game", methods=['GET', 'POST'])
def game():
    session['lifepoints'] = gamestate.character_stats.get('Health')
    action_name = session.get('final_action')
    room_name = session.get('room_name')
    david_lp = session.get('lifepoints')

    if request.method == "GET":

        if david_lp <= 0:
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

            action_instance = engine.Action(room, action)
            final_action = action_instance.determine_action()

            if action_instance.action_type != 'go':

                session['room_name'] = engine.name_room(room)
                session['final_action'] = final_action
            else:

                session['room_name'] = final_action
                session['final_action'] = False

        return redirect(url_for("game"))


app.secret_key = secrets.secret_app_key

if __name__ == "__main__":
    app.run(debug=True)
