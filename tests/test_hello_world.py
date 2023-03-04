def test_hello_world(client):
    response = client.get('/')
    assert response.data == b'Hello, World!'
