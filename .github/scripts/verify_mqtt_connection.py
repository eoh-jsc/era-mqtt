from time import sleep
import paho.mqtt.client as mqtt

SEND_MESSAGE = 'Hello, World!'

global success
success = False


def on_connect(client, userdata, flags, rc):
    print(f'Connected with result code {str(rc)}')
    assert rc == 0


def on_subscribe(client, userdata, mid, granted_qos):
    print(f'Subscribed with QoS: {str(granted_qos)}')
    assert granted_qos[0] == 0


def on_message(client, userdata, msg):
    print(f'Message receive: {msg.payload}')

    assert msg.payload == SEND_MESSAGE.encode()

    if msg.payload == SEND_MESSAGE.encode():
        global success
        success = True


def test_mqtt_connect_subscribe_listen(mqtt_server, mqtt_username):
    TOPIC = f'eoh/chip/{mqtt_username}/test'

    # Create an MQTT client and connect to the broker
    client = mqtt.Client(client_id=mqtt_username)
    client.username_pw_set(mqtt_username, mqtt_username)
    client.connect(mqtt_server, 1883)

    # Set up the callback functions
    client.on_connect = on_connect
    client.on_subscribe = on_subscribe
    client.on_message = on_message

    # Subscribe to a topic
    client.subscribe(TOPIC)

    client.loop_start()

    # Publish a message to the topic
    client.publish(TOPIC, SEND_MESSAGE)

    sleep(1)
    assert success is True
