from enum import Enum
from hashlib import sha256

import requests
from flask import redirect
from flask import Response
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from dotenv import dotenv_values
from flask import Flask
from flask import jsonify
from flask import request
from flask_basicauth import BasicAuth
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func
from werkzeug.exceptions import HTTPException

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


def create_app(env_filename, test):
    env = dotenv_values(env_filename)

    app = Flask(__name__)
    app.config.from_mapping(
        SQLALCHEMY_DATABASE_URI=env['SQLALCHEMY_DATABASE_URI'],
        BASIC_AUTH_USERNAME='',
        BASIC_AUTH_PASSWORD=env['API_KEY'],
        TESTING=test,
    )

    # initialize db and migrate
    db.init_app(app)
    migrate.init_app(app, db)
    basic_auth = BasicAuth(app)

    # admin
    app.config['FLASK_ADMIN_SWATCH'] = 'cerulean'
    admin = Admin(app, name='mqtt1 admin', template_mode='bootstrap3')

    class AuthException(HTTPException):  # pragma: no cover
        def __init__(self, message):
            super().__init__(
                message,
                Response(
                    'You could not be authenticated. Please refresh the page.', 401,
                    {'WWW-Authenticate': 'Basic realm="Login Required"'},
                ),
            )

    class MyModelView(ModelView):  # pragma: no cover
        def is_accessible(self):
            if not basic_auth.authenticate():
                raise AuthException('Not authenticated.')
            else:
                return True

        def inaccessible_callback(self, name, **kwargs):
            return redirect(basic_auth.challenge())

    class UserAdmin(MyModelView):
        column_display_pk = True

    class AclAdmin(MyModelView):
        column_display_pk = True

    admin.add_view(UserAdmin(Users, db.session))
    admin.add_view(AclAdmin(Acl, db.session))

    @app.route('/')
    def hello():
        return 'Hello, World!'

    @app.route('/healthcheck')
    def healthcheck():
        if not Users.query.count():
            raise Exception('No users in database')
        return 'OK'

    def _delete_all_acl_by_username(username):
        acls = Acl.query.filter_by(username=username).all()
        for acl in acls:
            db.session.delete(acl)
        db.session.commit()

    @app.route('/api/user', methods=['GET', 'POST'])
    @basic_auth.required
    def user_api():
        if request.method == 'GET':
            users = Users.query.all()
            return jsonify([user.to_dict() for user in users])

        username = request.json['username']
        password = request.json['password']

        # cloudmqtt {"error":"This username already exists"} 409
        user = Users.query.filter_by(username=username).first()
        if user:
            return 'This username already exists', 409

        username = username.strip()
        password_hash = sha256(password.encode('utf-8')).hexdigest()
        user = Users(
            username=username,
            password_hash=password_hash,
        )
        db.session.add(user)
        db.session.commit()
        return 'OK', 201

    def _kick_client(client_id):
        response = requests.delete(
            url=f"{env['EMQX_BASE_URL']}/clients/{client_id}",
            auth=(env['EMQX_USERNAME'], env['EMQX_PASSWORD']),
        )
        return response.status_code

    @app.route('/api/user/<username>', methods=['DELETE'])
    @basic_auth.required
    def user_delete(username):
        user = Users.query.filter_by(username=username).first()

        # cloudmqtt {"error":"No such user"} 404
        if not user:
            return 'No such user', 404

        db.session.delete(user)
        db.session.commit()
        _delete_all_acl_by_username(username)
        _kick_client(username)
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

        # cloudmqtt A rule matching {"type":"topic","pattern":"eoh/chip/123456/#","user":"123456"} already exists 400
        acl = Acl.query.filter_by(username=username, topic=pattern).first()
        if acl:
            return f'A rule matching {{"type":"topic","pattern":"{pattern}","user":"{username}"}} already exists', 400

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

    # cloudmqtt don't have this
    @app.route('/api/acl/<username>', methods=['DELETE'])
    @basic_auth.required
    def acl_delete(username):
        _delete_all_acl_by_username(username)
        return 'OK', 204

    return app
