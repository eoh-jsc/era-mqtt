from app import Acl
from app import Action
from app import Permission
from factories.acl import AclFactory


def test_get_acl(client):
    acl = AclFactory(action='all', permission='allow')
    response = client.get("/api/acl")
    assert response.status_code == 200
    assert response.json == [{
        'action': acl.action,
        'permission': acl.permission,
        'topic': acl.topic,
        'username': acl.username,
    }]


def _test_add_acl(client, read, write):
    response = client.post("/api/acl", json={
        "username": "User 1",
        "pattern": "pattern_1",
        "read": read,
        "write": write,
    })
    assert response.status_code == 201
    assert response.data == b'OK'

    acl = Acl.query.first()
    assert Acl.query.count() == 1
    assert acl.username == "User 1"
    assert acl.topic == "pattern_1"
    return acl


def test_add_acl_read(client):
    acl = _test_add_acl(client, True, False)
    assert acl.action == Action.subscribe
    assert acl.permission == Permission.allow


def test_add_acl_write(client):
    acl = _test_add_acl(client, False, True)
    assert acl.action == Action.publish
    assert acl.permission == Permission.allow


def test_add_acl_read_write(client):
    acl = _test_add_acl(client, True, True)
    assert acl.action == Action.all
    assert acl.permission == Permission.allow


def test_add_acl_no_read_write(client):
    acl = _test_add_acl(client, False, False)
    assert acl.action == Action.all
    assert acl.permission == Permission.deny
