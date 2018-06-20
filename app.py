from flask import Flask, session, redirect, url_for, escape, request
from flask import render_template
from david_web import engine
from david_web import gamestate
from david_web import planisphere

app = Flask(__name__)


@app.route("/")
def index():
    # this is used to "setup" the session with starting values
    session['room_name'] = planisphere.START
    session['final_action'] = False
    return redirect(url_for("game"))


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
            room = engine.match_Room(room_name)
            return render_template("show_room.html", room=room, action_name=action_name)
        else:
            # why is there here? do you need it?
            return render_template("you_died.html")

    else:
        action = request.form.get('action')

        if room_name and action:
            room = engine.match_Room(room_name)

            action_instance = engine.Action(room, action)
            final_action = action_instance.determine_action()

            if action_instance.action_type != 'go':

                session['room_name'] = engine.name_room(room)
                session['final_action'] = final_action
            else:

                session['room_name'] = final_action
                session['final_action'] = False

        return redirect(url_for("game"))


app.secret_key = 'uYstR*b27j6w7EztZl@1MH#Xtr0LkD'

if __name__ == "__main__":
    app.run(debug=True)
