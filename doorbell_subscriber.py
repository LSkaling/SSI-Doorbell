import paho.mqtt.client as mqtt
from dotenv import load_dotenv
import os

load_dotenv()

username = os.getenv("MQTT_USERNAME")
password = os.getenv("MQTT_PASSWORD")
broker_ip = os.getenv("BROKER_IP")

broker = broker_ip  # Replace with your computer's IP
port = 1883
topic = "test/topic"

def on_message(client, userdata, msg):
    print(f"Received message: {msg.payload.decode()} on topic {msg.topic}")
    

client = mqtt.Client()
client.username_pw_set(username, password)
client.on_message = on_message
client.connect(broker, port)

client.subscribe(topic)
print("Subscribed to topic:", topic)
client.loop_forever()
