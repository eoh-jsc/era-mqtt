def test_request_hello_world(client):
    response = client.get("/")
    assert b'Hello, World!' in response.data
