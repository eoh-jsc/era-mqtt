from freezegun import freeze_time
from datetime import datetime

from factories.users import UsersFactory
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


def test_delete_user(client, auth_user):
    user = UsersFactory()
    response = client.delete(f'/api/user/{user.username}', headers=auth_user)
    assert response.status_code == 204
    assert response.data == b''
    assert Users.query.count() == 0
