import os
import json
from flask import Flask, session, render_template, request, redirect, url_for
from flask_session import Session
from flask_socketio import SocketIO, emit
from channel import Channel

app = Flask(__name__)

app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
socketio = SocketIO(app)

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

channels = []

@app.route("/")
def login():
    if "user" not in session.keys():
        return render_template("login.html")
    else:
        return redirect(url_for("home"))

@app.route("/login_user/", methods=["POST"])
def login_user():
    session["user"] = request.form.get("user")
    return redirect(url_for("home"))
    
@app.route("/home/")
def home():
    if "user" not in session.keys():
        return redirect(url_for("login"))
    elif "recent" in session.keys():
        return redirect(url_for("channel", name=session["recent"]))
    else:
        return render_template("home.html", user=session["user"])

@app.route("/logout/")
def logout():
    session.pop("user", None)
    return redirect(url_for("home"))

@app.route("/channels/")
def channel_list():
    return render_template("channel_list.html", channels=channels)

@app.route("/get_channels/")
def get_channels():
    return {"channels": [c.get_json() for c in channels]}

@app.route("/create_channel/", methods=["POST"])
def create_channel():
    name = request.form.get("name")
    if name not in [ c.name for c in channels ]:
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
    return render_template("channel.html", name=name, user=session['user'])

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

