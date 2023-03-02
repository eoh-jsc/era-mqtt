import pytest

from app import create_app
from app import db


@pytest.fixture()
def app():
    app = create_app("sqlite://")
    app.config["TESTING"] = True

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


@pytest.fixture()
def runner(app):
    return app.test_cli_runner()
