from hashlib import sha256
from enum import Enum
from time import sleep

from dotenv import dotenv_values
from flask import Flask
from flask import jsonify
from flask import request
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_basicauth import BasicAuth
from paho.mqtt import client

from sqlalchemy.sql import func

db = SQLAlchemy()
migrate = Migrate()


class Permission(Enum):
    allow = 'allow'
    deny = 'deny'


class Action(Enum):
    publish = 'publish'
    subscribe = 'subscribe'
    all = 'all'


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


class Users(db.Model):
    username = db.Column(db.String, unique=True, primary_key=True, nullable=False)
    password_hash = db.Column(db.String, default='', nullable=False)
    salt = db.Column(db.String, default='', nullable=False)
    is_superuser = db.Column(db.Boolean, default=False, nullable=False)
    time_created = db.Column(db.DateTime(timezone=True), server_default=func.now())

    def to_dict(self):
        return {
            'username': self.username,
            'time_created': self.time_created,
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
            'permission': str(self.permission),
            'action': str(self.action),
        }


class MqttConnection:  # pragma: no cover
    success = False

    def __init__(self, mqtt_server, mqtt_username):
        self.client = client.Client(client_id=mqtt_username)
        self.client.username_pw_set(mqtt_username, mqtt_username)
        self.client.connect(mqtt_server, 1883)

        self.client.on_connect = self.on_connect
        self.client.on_subscribe = self.on_subscribe
        self.client.on_message = self.on_message

        self.client.loop_start()

    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            self.success = True

    def on_subscribe(self, client, userdata, mid, granted_qos):
        print(f'Subscribed with QoS: {str(granted_qos)}')

    def on_message(self, client, userdata, msg):
        print(f'Message receive: {msg.payload}')

    def disconnect(self):
        self.client.disconnect()


def create_app(env_filename, test):
    env = dotenv_values(env_filename)

    app = Flask(__name__)
    app.config.from_mapping(
        SQLALCHEMY_DATABASE_URI=env['SQLALCHEMY_DATABASE_URI'],
        BASIC_AUTH_USERNAME='',
        BASIC_AUTH_PASSWORD=env['API_KEY'],
        TESTING=test,
    )

    db.init_app(app)
    migrate.init_app(app, db)
    basic_auth = BasicAuth(app)

    @app.route('/')
    def hello():
        return 'Hello, World!'

    @app.route('/healthcheck')
    def healthcheck():
        if not Users.query.count():
            raise Exception('No users in database')

        client = MqttConnection(env['MQTT_SERVER'], env['MQTT_USERNAME'])

        sleep(3)  # TODO optimize by thread
        if not client.success:
            raise Exception('MQTT connection failed')

        client.disconnect()
        return 'OK'

    @app.route('/api/user', methods=['GET', 'POST'])
    @basic_auth.required
    def user_api():
        if request.method == 'GET':
            users = Users.query.all()
            return jsonify([user.to_dict() for user in users])

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

    @app.route('/api/user/<username>', methods=['DELETE'])
    @basic_auth.required
    def user_delete(username):
        user = Users.query.filter_by(username=username).one()
        db.session.delete(user)
        db.session.commit()
        return 'OK', 204

    @app.route('/api/acl', methods=['GET', 'POST'])
    @basic_auth.required
    def acl_api():
        if request.method == 'GET':
            acls = Acl.query.all()
            return jsonify([acl.to_dict() for acl in acls])

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

    @app.route('/api/acl/<username>', methods=['DELETE'])
    @basic_auth.required
    def acl_delete(username):
        acls = Acl.query.filter_by(username=username).all()
        for acl in acls:
            db.session.delete(acl)
        db.session.commit()
        return 'OK', 204

    return app
