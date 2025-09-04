import requests_mock


def _create_rule(client, auth_user):
    response = client.post('/api/rule', json={
        'id': 'test_id_republish',
        'sql': "SELECT payload, topic FROM 'eoh/chip/chip_code/#'",
        'actions': [{
            'function': 'republish',
            'args': {
                'topic': '${topic}',
                'payload': '${payload}',
            }
        }],
        'enable': True
    }, headers=auth_user)
    return response


def test_create_rule(client, auth_user):
    with requests_mock.Mocker() as m:
        m.post('http://localhost:18083/api/v5/rules', status_code=201, text='OK')

        response = _create_rule(client, auth_user)
        assert response.status_code == 201
        assert response.data == b'Created'

        assert m.call_count == 1
        assert m.request_history[0].method == 'POST'
        assert m.request_history[0].url == 'http://localhost:18083/api/v5/rules'


def test_create_rule_then_update_when_already_exists(client, auth_user):
    with requests_mock.Mocker() as m:
        m.post('http://localhost:18083/api/v5/rules', status_code=400, text='Already exists')
        m.put('http://localhost:18083/api/v5/rules/test_id_republish', status_code=200, text='OK')

        response = _create_rule(client, auth_user)
        assert response.status_code == 200
        assert response.data == b'OK'

        assert m.call_count == 2
        assert m.request_history[0].method == 'POST'
        assert m.request_history[0].url == 'http://localhost:18083/api/v5/rules'
        assert m.request_history[1].method == 'PUT'
        assert m.request_history[1].url == 'http://localhost:18083/api/v5/rules/test_id_republish'


def test_create_rule_failed(client, auth_user):
    with requests_mock.Mocker() as m:
        m.post('http://localhost:18083/api/v5/rules', status_code=500, text='Internal Error')

        response = _create_rule(client, auth_user)
        assert response.status_code == 500
        assert response.data == b'Internal Error'

        assert m.call_count == 1
        assert m.request_history[0].method == 'POST'
        assert m.request_history[0].url == 'http://localhost:18083/api/v5/rules'


def test_create_rule_but_no_id(client, auth_user):
    response = client.post('/api/rule', json={
        'sql': "SELECT payload, topic FROM 'eoh/chip/chip_code/#'",
        'actions': [{
            'function': 'republish',
            'args': {
                'topic': '${topic}',
                'payload': '${payload}',
            }
        }],
        'enable': True
    }, headers=auth_user)
    assert response.status_code == 400
    assert response.data == b'Field "id" is required'


def test_delete_rule(client, auth_user):
    with requests_mock.Mocker() as m:
        m.delete('http://localhost:18083/api/v5/rules/test_id_republish', status_code=204, text='')

        response = client.delete('/api/rule/test_id_republish', headers=auth_user)
        assert response.status_code == 204
        assert response.data == b''

        assert m.call_count == 1
        assert m.request_history[0].method == 'DELETE'
        assert m.request_history[0].url == 'http://localhost:18083/api/v5/rules/test_id_republish'
