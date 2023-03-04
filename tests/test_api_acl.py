from factories.acl import AclFactory
from init_app import Acl
from init_app import Action
from init_app import Permission


def test_get_acl(client, auth_user):
    acl = AclFactory(action='all', permission='allow')
    response = client.get("/api/acl", headers=auth_user)
    assert response.status_code == 200
    assert response.json == [{
        'action': acl.action,
        'permission': acl.permission,
        'topic': acl.topic,
        'username': acl.username,
    }]


def _test_add_acl(client, auth_user, read, write):
    response = client.post("/api/acl", json={
        "username": "User 1",
        "pattern": "pattern_1",
        "read": read,
        "write": write,
    }, headers=auth_user)
    assert response.status_code == 201
    assert response.data == b'OK'

    acl = Acl.query.first()
    assert Acl.query.count() == 1
    assert acl.username == "User 1"
    assert acl.topic == "pattern_1"
    return acl


def test_add_acl_read(client, auth_user):
    acl = _test_add_acl(client, auth_user, True, False)
    assert acl.action == Action.subscribe
    assert acl.permission == Permission.allow


def test_add_acl_write(client, auth_user):
    acl = _test_add_acl(client, auth_user, False, True)
    assert acl.action == Action.publish
    assert acl.permission == Permission.allow


def test_add_acl_read_write(client, auth_user):
    acl = _test_add_acl(client, auth_user, True, True)
    assert acl.action == Action.all
    assert acl.permission == Permission.allow


def test_add_acl_no_read_write(client, auth_user):
    acl = _test_add_acl(client, auth_user, False, False)
    assert acl.action == Action.all
    assert acl.permission == Permission.deny


def test_delete_acl(client, auth_user):
    acl = AclFactory(username='User 1')
    AclFactory(username='User 1')  # another acl same user
    response = client.delete(f"/api/acl/{acl.username}", headers=auth_user)
    assert response.status_code == 204
    assert response.data == b''
    assert Acl.query.count() == 0
