import os
import urllib2
import requests
from flask import Flask, redirect, render_template, request
from flask_sqlalchemy import SQLAlchemy
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
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
    whitelist = User.query.all()
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
    
    
    if checkIpWhitelist(yourIP):
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
    try:
        txt = urllib2.urlopen("http://view.light-speed.com/teamspeak3.php?IP=ts.discordantgamers.com&PORT=9987&QUERY=10011&UID=763660&display=none&font=12px", timeout=1).read()
    except:
        return False
    if 'Error' in txt:
        return False
    else:
        return True
def checkIpWhitelist(ip):
    whitelist = User.query.all()
    if any(ip in s.ip for s in whitelist):
        return True
    else:
        return False
def ipServerUp(ip):
    try:
        txt = urllib2.urlopen("http://view.light-speed.com/teamspeak3.php?IP=" + ip + "&PORT=9987&QUERY=10011&UID=763660&display=none&font=12px", timeout=2).read()
    except:
        return False
    if 'Error' in txt:
        return False
    else:
        return True
@app.route("/whitelist")
def whitelist():
    white = User.query.all()
    whitestring = ''
    for s in white:
        whitestring += s.ip + '%'
    if request.headers.getlist("X-Forwarded-For"):
        yourIP = request.headers.getlist("X-Forwarded-For")[0]
    else:
        yourIP = request.remote_addr
    whitestring += yourIP + '$'
    return whitestring

@app.route("/setIP", methods=['POST'])
def setIP():
    auth = False
    password = ''
    ip = ''

    try:
        ip = request.form['ip']
        password = request.form['password']
    except :
        try:
            ip = request.args.get('ip', '')
            password = request.args.get('password', '')
        except :
            return ' failed to find form info or args info '

    if password == os.environ['PASSWORD']:
        auth = True
    if remoteServerUp():
        if auth == False:
            return 'The ip already points to an online server and no overide password supplied'
    if ipServerUp(ip) == False:
        return 'The target server is offline'
    #at this point we know the target server is online and we have permission to change the current servers ip away
    if checkIpWhitelist(ip) == False:
        #ip not on the whitelist
        if auth:
            #we are authorized so we add the ip to the whitelist
            newuser = User(ip)
            db.session.add(newuser)
            db.session.commit()
        else:
            #we are not authorized or whitelisted so we error boys
            return 'Not whitelisted or authorized to whitelist (ask admin for password)'
    payload = {'hostname': 'ts.discordantgamers.com', 'myip': ip}
    r = requests.post('https://' + os.environ['DNSAPI_USERNAME'] + ':' + os.environ['DNSAPI_PASSWORD'] + '@domains.google.com/nic/update', params=payload)
    return r.text
#if __name__ == "__main__":
#    app.run()
