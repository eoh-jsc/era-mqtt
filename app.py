import enum
import os
from hashlib import sha256

from flask import Flask
from flask import request
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

from sqlalchemy.sql import func

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://root:password@postgres/emqx'
db = SQLAlchemy(app)
migrate = Migrate(app, db)

API_KEY = os.getenv('API_KEY')


class Permission(enum.Enum):
    allow = "allow"
    deny = "deny"


class Action(enum.Enum):
    publish = "publish"
    subscribe = "subscribe"
    all = "all"


# TODO username as primary key
class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, unique=True, nullable=False)
    password_hash = db.Column(db.String, default='', nullable=False)
    salt = db.Column(db.String, default='', nullable=False)
    is_superuser = db.Column(db.Boolean, default=False, nullable=False)
    time_created = db.Column(db.DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        return self.username


class Acl(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, default='', nullable=False)
    ipaddress = db.Column(db.String, default='', nullable=False)
    clientid = db.Column(db.String, default='', nullable=False)
    topic = db.Column(db.String, nullable=False)
    permission = db.Column(db.Enum(Permission))
    action = db.Column(db.Enum(Action))


@app.route("/")
def hello():
    return "Hello, World!"


@app.route("/api/user", methods=['POST'])
def user_create():
    if request.headers.get('Authorization') != API_KEY:
        return 'Wrong api key', 403

    username = request.json['username']
    password = request.json['password']

    username = username.strip()
    password_hash = sha256(password.encode('utf-8')).hexdigest()

    user = Users(
        username=username,
        password_hash=password_hash,
    )

    db.session.add(user)
    db.session.commit()
    return 'OK', 201


@app.route("/api/user/<username>", methods=['DELETE'])
def user_delete(username):
    if request.headers.get('Authorization') != API_KEY:
        return 'Wrong api key', 403

    user = Users.query.filter_by(username=username).one()

    db.session.delete(user)
    db.session.commit()
    return 'OK', 204


def get_action_and_permission(read, write):
    action = 'all'
    permission = 'deny'

    if read:
        action = 'subscribe'
        permission = 'allow'
    if write:
        action = 'publish'
        permission = 'allow'
    if read and write:
        action = 'all'
        permission = 'allow'

    return action, permission


@app.route("/api/acl", methods=['POST'])
def acl_create():
    if request.headers.get('Authorization') != API_KEY:
        return 'Wrong api key', 403

    username = request.json['username']
    pattern = request.json['pattern']
    read = request.json['read']
    write = request.json['write']

    action, permission = get_action_and_permission(read, write)

    acl = Acl(
        username=username,
        topic=pattern,
        permission=permission,
        action=action,
    )
    db.session.add(acl)
    db.session.commit()
    return 'OK', 201


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
