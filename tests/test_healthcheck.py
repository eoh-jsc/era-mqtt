import pytest

from factories.users import UsersFactory


def test_healthcheck_without_users(client):
    with pytest.raises(Exception) as excinfo:
        client.get('/healthcheck')
        assert 'No users in database' in str(excinfo.value)


def test_healthcheck_success(client):
    UsersFactory()
    response = client.get('/healthcheck')
    assert response.status_code == 200
    assert response.data == b'OK'
