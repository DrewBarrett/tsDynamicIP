import os
import urllib2
from flask import Flask, redirect, render_template, request
from flask_sqlalchemy import SQLAlchemy
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ip = db.Column(db.String(80), unique=True)

    def __init__(self, ip):
        self.ip = ip

    def __repr__(self):
        return '<User %r>' % self.ip


@app.route("/")
def hello():
    remoteServerStatus = None
    yourServerStatus = None
    yourIP = request.remote_addr
    txt = urllib2.urlopen("http://view.light-speed.com/teamspeak3.php?IP=ts.discordantgamers.com&PORT=9987&QUERY=10011&UID=763660&display=none&font=12px").read()
    if 'Error' in txt:
        remoteServerStatus = 'offline'
    else:
        remoteServerStatus = 'online'
    txt = urllib2.urlopen("http://view.light-speed.com/teamspeak3.php?IP=" + yourIP + "&PORT=9987&QUERY=10011&UID=763660&display=none&font=12px").read()
    if 'Error' in txt:
        yourServerStatus = 'offline'
    else:
        yourServerStatus = 'online'

    return render_template('template.html', currentServerStatus=remoteServerStatus,yourServerStatus=yourServerStatus,yourIP=yourIP)

#if __name__ == "__main__":
#    app.run()
