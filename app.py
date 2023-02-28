import os
import json
from hashlib import sha256
from enum import Enum

from flask import Flask
from flask import jsonify
from flask import request
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_basicauth import BasicAuth

from sqlalchemy.sql import func

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://root:password@postgres/emqx'
app.config['BASIC_AUTH_USERNAME'] = ''
app.config['BASIC_AUTH_PASSWORD'] = os.getenv('API_KEY')

db = SQLAlchemy(app)
migrate = Migrate(app, db)

basic_auth = BasicAuth(app)


class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Enum):
            return obj.value
        return super().default(obj)


class Permission(Enum):
    allow = "allow"
    deny = "deny"


class Action(Enum):
    publish = "publish"
    subscribe = "subscribe"
    all = "all"


class Users(db.Model):
    username = db.Column(db.String, unique=True, primary_key=True, nullable=False)
    password_hash = db.Column(db.String, default='', nullable=False)
    salt = db.Column(db.String, default='', nullable=False)
    is_superuser = db.Column(db.Boolean, default=False, nullable=False)
    time_created = db.Column(db.DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        return self.username

    def to_dict(self):
        return {
            'username': self.username,
            'time_created': self.time_created
        }


class Acl(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, default='', nullable=False)
    ipaddress = db.Column(db.String, default='', nullable=False)
    clientid = db.Column(db.String, default='', nullable=False)
    topic = db.Column(db.String, nullable=False)
    permission = db.Column(db.Enum(Permission))
    action = db.Column(db.Enum(Action))

    def to_dict(self):
        return {
            'username': self.username,
            'topic': self.topic,
            'permission': self.permission,
            'action': self.action
        }


@app.route("/")
def hello():
    return "Hello, World!!!"


@app.route("/api/user", methods=['GET', 'POST'])
@basic_auth.required
def user_create():
    if request.method == 'GET':
        users = Users.query.all()
        return jsonify([user.to_dict() for user in users])
    else:
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
@basic_auth.required
def user_delete(username):
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


@app.route("/api/acl", methods=['GET', 'POST'])
@basic_auth.required
def acl_create():
    if request.method == 'GET':
        acls = Acl.query.all()
        data = json.dumps([acl.to_dict() for acl in acls], cls=CustomJSONEncoder)
        return jsonify(json.loads(data))
    else:
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
