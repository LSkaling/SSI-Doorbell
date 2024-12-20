import paho.mqtt.client as mqtt
from dotenv import load_dotenv
import os

load_dotenv()

username = os.getenv("MQTT_USERNAME")
password = os.getenv("MQTT_PASSWORD")
broker = os.getenv("BROKER_IP")

broker = broker  # Replace with your computer's IP
port = 1883
topic = "test/topic"

client = mqtt.Client()
client.username_pw_set(username, password)
client.connect(broker, port)

client.publish(topic, "Hello from Python Publisher!")
print("Message published.")
