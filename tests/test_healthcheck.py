import pytest

from factories.users import UsersFactory


def _test_healthcheck_with_user(client, mocker, success):
    UsersFactory()

    mocker.patch('init_app.sleep', return_value=None)
    mqtt_connection_class = mocker.patch('init_app.MqttConnection')
    mock_mqtt_connection = mqtt_connection_class.return_value
    mock_mqtt_connection.success = success

    response = client.get('/healthcheck')

    return response, mock_mqtt_connection


def test_healthcheck_success(client, mocker):
    response, mock_mqtt_connection = _test_healthcheck_with_user(client, mocker, True)
    assert response.status_code == 200
    assert response.data == b'OK'
    mock_mqtt_connection.disconnect.assert_called_once()


def test_healthcheck_fail(client, mocker):
    with pytest.raises(Exception) as excinfo:
        response, mock_mqtt_connection = _test_healthcheck_with_user(client, mocker, False)
        assert 'MQTT connection failed' in str(excinfo.value)
        mock_mqtt_connection.disconnect.assert_not_called()


def test_healthcheck_fail_without_users(client):
    with pytest.raises(Exception) as excinfo:
        client.get('/healthcheck')
        assert 'No users in database' in str(excinfo.value)
