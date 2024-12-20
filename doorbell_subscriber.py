#!/home/admin/SSI-Doorbell/venv/bin/python3

import paho.mqtt.client as mqtt
from dotenv import load_dotenv
import os
import pygame

load_dotenv()

username = os.getenv("MQTT_USERNAME")
password = os.getenv("MQTT_PASSWORD")
broker_ip = os.getenv("BROKER_IP")

client_id = os.getenv("CLIENT_ID")
status_topic = f"status/{client_id}"
command_topic = f"commands/{client_id}"

broker = broker_ip  # Replace with your computer's IP
port = 1883
topic = "test/topic"

def on_connect(client, userdata, flags, rc):
    print(f"{client_id} connected to the broker.")
    # Publish an "online" status when the client connects
    client.publish(status_topic, "online", retain=True)
    # Subscribe to commands for this specific Pi
    client.subscribe(command_topic)
    client.subscribe(topic)
    print(f"Subscribed to {command_topic}")

def on_disconnect(client, userdata, rc):
    print(f"{client_id} disconnected from the broker.")

def on_message(client, userdata, msg):
    print(f"Received message: {msg.payload.decode()} on topic {msg.topic}")  
    pygame.mixer.init()
    pygame.mixer.music.load("/home/admin/SSI-Doorbell/long-doorbell.mp3")      
    pygame.mixer.music.play()


client = mqtt.Client()
client.username_pw_set(username, password)
client.on_message = on_message
client.on_connect = on_connect
client.on_disconnect = on_disconnect


# Set Last Will and Testament
client.will_set(status_topic, "offline", qos=1, retain=True)

client.connect(broker, port, 60) #checks every 5 seconds

print("Subscribed to topic:", topic)
client.loop_forever()
