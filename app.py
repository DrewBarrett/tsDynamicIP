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
    whitelisted = False
    #yourIP = request.environ['REMOTE_ADDR']
    if request.headers.getlist("X-Forwarded-For"):
        yourIP = request.headers.getlist("X-Forwarded-For")[0]
    else:
        yourIP = request.remote_addr
    if remoteServerUp():
        remoteServerStatus = 'online'
    else:
        remoteServerStatus = 'offline'
    if ipServerUp(yourIP):
        yourServerStatus = 'online'
    else:
        yourServerStatus = 'offline'
    whitelist = User.query.all()
    if any(yourIP in s.ip for s in whitelist):
        whitelisted = True
        yourServerStatus += ' and is on the whitelist: '
    else:
        whitelisted = False
        yourServerStatus += ' and is not on the whitelist: '
    for s in whitelist:
        online = 'offline'
        if ipServerUp(s.ip):
            online = 'online'
        yourServerStatus += ' ' + s.ip +  '(' + online + '),'

    if 'offline' in remoteServerStatus:
        return render_template('updateIP.html', currentServerStatus=remoteServerStatus,yourServerStatus=yourServerStatus,yourIP=yourIP)
    return render_template('updateIP.html', currentServerStatus=remoteServerStatus,yourServerStatus=yourServerStatus,yourIP=yourIP)
def remoteServerUp():
    txt = urllib2.urlopen("http://view.light-speed.com/teamspeak3.php?IP=ts.discordantgamers.com&PORT=9987&QUERY=10011&UID=763660&display=none&font=12px").read()
    if 'Error' in txt:
        return False
    else:
        return True
def ipServerUp(ip):
    txt = urllib2.urlopen("http://view.light-speed.com/teamspeak3.php?IP=" + ip + "&PORT=9987&QUERY=10011&UID=763660&display=none&font=12px").read()
    if 'Error' in txt:
        return False
    else:
        return True

@app.route("/setIP", methods=['POST'])
def setIP():
    if remoteServerUp():
        if request.form['password'] != os.environ['PASSWORD']:
            return 'The ip already points to an online server'
    if ipServerUp(request.form['ip']) == False:
        return 'The requested ip does not have an accessable ts server'
    return 'failed to set ip'
#if __name__ == "__main__":
#    app.run()
