from datetime import datetime

import requests_mock
from freezegun import freeze_time

from factories.acl import AclFactory
from factories.users import UsersFactory
from init_app import Acl
from init_app import Users


@freeze_time('2012-01-01')
def test_get_user(client, auth_user):
    user = UsersFactory(time_created=datetime.now())  # TODO mock datetime without passed it as argument
    response = client.get('/api/user', headers=auth_user)
    assert response.status_code == 200
    assert response.json == [{
        'time_created': 'Sun, 01 Jan 2012 00:00:00 GMT',
        'username': user.username,
    }]


def test_add_user(client, auth_user):
    response = client.post('/api/user', json={'username': 'User 1', 'password': 'password_1'}, headers=auth_user)
    assert response.status_code == 201
    assert response.data == b'OK'

    user = Users.query.first()
    assert Users.query.count() == 1
    assert user.username == 'User 1'


def test_add_user_but_already_exist(client, auth_user):
    username = 'User 1'
    UsersFactory(username=username)
    response = client.post('/api/user', json={'username': username, 'password': 'password_1'}, headers=auth_user)
    assert response.status_code == 409
    assert response.data == b'This username already exists'


def test_delete_user(client, auth_user):
    with requests_mock.Mocker() as m:
        user = UsersFactory()
        AclFactory(username=user.username)
        m.delete(f'http://localhost:18083/api/v5/clients/{user.username}')
        m.delete(f'http://localhost:18083/api/v5/rules/{user.username}')

        response = client.delete(f'/api/user/{user.username}', headers=auth_user)
        assert response.status_code == 204
        assert response.data == b''
        assert Users.query.count() == 0
        assert Acl.query.count() == 0

        assert m.call_count == 2
        assert m.request_history[0].method == 'DELETE'
        assert m.request_history[0].url == f'http://localhost:18083/api/v5/clients/{user.username}'
        assert m.request_history[1].method == 'DELETE'
        assert m.request_history[1].url == f'http://localhost:18083/api/v5/rules/{user.username}'


def test_delete_user_but_no_exist(client, auth_user):
    with requests_mock.Mocker() as m:
        response = client.delete('/api/user/USER_NOT_EXIST', headers=auth_user)
        assert response.status_code == 404
        assert response.data == b'No such user'

        assert m.call_count == 0
