import pytest
import base64

from init_app import create_app
from init_app import db


@pytest.fixture()
def app():
    app = create_app('.env.test', test=True)

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
    credentials = f'{username}:{password}'.encode('utf-8')
    token = base64.b64encode(credentials).decode('utf-8')
    return {'Authorization': f'Basic {token}'}


def pytest_addoption(parser):
    parser.addoption('--mqtt_server', action='store', default='default input1')
    parser.addoption('--mqtt_username', action='store', default='default input2')


@pytest.fixture
def mqtt_server(request):
    return request.config.getoption('--mqtt_server')


@pytest.fixture
def mqtt_username(request):
    return request.config.getoption('--mqtt_username')


@pytest.fixture()
def runner(app):
    return app.test_cli_runner()
