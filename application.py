import os
import json
from flask import Flask, session, render_template, request, redirect, url_for
from flask_session import Session
from flask_socketio import SocketIO, emit
from channel import Channel, PrivateChannel

app = Flask(__name__)

app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
socketio = SocketIO(app)

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

channels = []
users = []

@app.route("/")
def login():
    if "user" not in session.keys():
        return render_template("login.html")
    else:
        return redirect(url_for("home"))

@app.route("/login_user/", methods=["POST"])
def login_user():
    user = request.form.get("user")
    if user not in users and len(user) > 0:
        session["user"] = user
        users.append(user)
        return redirect(url_for("home"))
    else:
        return render_template("login.html", error=True)
    
@app.route("/home/")
def home():
    if "user" not in session.keys():
        return redirect(url_for("login"))
    elif "recent" in session.keys():
        if session["recent"] in channels:
            return redirect(url_for("channel", name=session["recent"]))
        else:
            return render_template("home.html", user=session["user"])
    else:
        return render_template("home.html", user=session["user"])

@app.route("/logout/")
def logout():
    session.pop("user", None)
    return redirect(url_for("home"))

@app.route("/channels/")
def channel_list():
    return render_template("channel_list.html")

@app.route("/get_channels/")
def get_channels():
    user = request.args.get("user")
    public_channels = [c.get_json() for c in channels if not c.private]
    private_channels = [c.get_json() for c in channels if c.private and user in c.users]
    return {"public": public_channels, "private": private_channels}

@app.route("/get_users/")
def get_users():
    return json.dumps({"users": users})

@app.route("/create_channel/", methods=["POST"])
def create_channel():
    params = request.json
    name = params['name']
    private = params['private']
    if name not in [ c.name for c in channels ] and len(name) > 0:
        if private:
            users = params['users']
            newChannel = PrivateChannel(name, users)
            channels.append(newChannel)
        else:
            newChannel = Channel(name)
            channels.append(newChannel)
        return "Did it!"
    else:
         return ("Couldn't do it!", 406)

@app.route("/channels/<name>")
def channel(name):
    if 'user' not in session.keys():
        return "MUST BE LOGGED IN!"
    session["recent"] = name

    users = []
    for channel in channels:
        if channel.name == name and channel.private:
            users = channel.users
            break

    return render_template("channel.html", name=name, user=session['user'], userlist=users)

@app.route("/channels/<name>/messages/", methods=["GET", "POST"])
def messages(name):
    for c in channels:
        if c.name == name:
            if request.method == "GET":
                return c.get_json()
            else: # POST
                message = request.form.get("message")
                user = request.form.get("user")
                c.add_message(user, message)
                return "Added message!"
    return ("Channel not found!", 404)

@app.route("/reset/")
def reset():
    session.pop('user', None)
    return redirect(url_for('home'))