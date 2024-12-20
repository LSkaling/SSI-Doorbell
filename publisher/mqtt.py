import paho.mqtt.client as mqtt
import os

node_states = {}

def setup_mqtt(slack_app):
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()

    broker_ip = os.getenv("BROKER_IP")
    username = os.getenv("MQTT_USERNAME")
    password = os.getenv("MQTT_PASSWORD")
    port = 1883
    status_topic = "status/#"

    def on_message(client, userdata, message):
        node_id = message.topic.split("/")[-1]
        payload = message.payload.decode()
        print(f"Status update: {message.topic} -> {payload}")

        global node_states
        node_states[node_id] = payload

    client = mqtt.Client()
    client.username_pw_set(username, password)
    client.on_message = on_message
    client.connect(broker_ip, port)
    client.loop_start()
    client.subscribe(status_topic)
    print(f"Subscribed to {status_topic}")

    return client, node_states
