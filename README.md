to add ip to whitelist:
heroku run python --app tsdiscordant
>>> from app import db
>>> from app import User
>>> newuser = User('ipaddr')
>>> db.session.add(newuser)
>>> db.session.commit()