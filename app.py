from flask import Flask, session, redirect, url_for, escape, request
from flask import render_template
from david_web import planisphere

app = Flask(__name__)

@app.route("/")
def index():
    # this is used to "setup" the session with starting values
    session['room_name'] = planisphere.START
    return redirect(url_for("game"))

@app.route("/game", methods=['GET', 'POST'])
def game():
    room_name = session.get('room_name')

    if request.method == "GET":
        if room_name:
            room = planisphere.load_room(room_name)
            return render_template("show_room.html", room=room)
        else:
            # why is there here? do you need it?
            return render_template("you_died.html")

    else:
        action = request.form.get('action')

        if room_name and action:
            room = planisphere.load_room(room_name)
            action_instance = planisphere.Action(room, action)
            final_action = action_instance.determine_action()
            print(">>>> final action", final_action)

            if action_instance.action_type != 'go':
                session['room_name'] = planisphere.name_room(room)
            else:
                session['room_name'] = planisphere.name_room(final_action)

        return redirect(url_for("game"))



app.secret_key = 'uYstR*b27j6w7EztZl@1MH#Xtr0LkD'

if __name__ == "__main__":
    app.run()
