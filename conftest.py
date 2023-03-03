import pytest
import base64

from flask.cli import load_dotenv

from init_app import create_app
from init_app import db


@pytest.fixture()
def app():
    load_dotenv('.env.test')
    app = create_app(db_path="sqlite://", test=True)

    print('xxxxx', app.config)

    with app.app_context():
        db.create_all()
        yield app

        # other setup can go here
        # app
        # clean up / reset resources here


@pytest.fixture()
def client(app):
    client = app.test_client()
    yield client


@pytest.fixture
def auth_user():
    username = ''
    password = 'Token'
    credentials = f"{username}:{password}".encode('utf-8')
    token = base64.b64encode(credentials).decode('utf-8')
    return {'Authorization': f'Basic {token}'}


@pytest.fixture()
def runner(app):
    return app.test_cli_runner()
