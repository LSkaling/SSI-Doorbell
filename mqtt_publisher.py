from flask import Flask, request
from slack_bolt import App
from slack_bolt.adapter.flask import SlackRequestHandler
from dotenv import load_dotenv
import os
import paho.mqtt.client as mqtt

load_dotenv()

# Flask app for handling requests
app = Flask(__name__)
bolt_app = App(
    token=os.getenv("SLACK_BOT_TOKEN"),
    signing_secret=os.getenv("SLACK_SIGNING_SECRET"))
handler = SlackRequestHandler(bolt_app)

# MQTT setup
username = os.getenv("MQTT_USERNAME")
password = os.getenv("MQTT_PASSWORD")
broker_ip = os.getenv("BROKER_IP")
port = 1883
topic = "test/topic"
status_topic = "status/#"  # Wildcard to monitor all status topics

# MQTT Callbacks
def on_message(client, userdata, message):
    print(f"Status update: {message.topic} -> {message.payload.decode()}")
    bolt_app.client.chat_postMessage(
        channel="C7F3VVB1S",
        text=f"Status update: {message.topic} -> {message.payload.decode()}")

# Initialize MQTT client
client = mqtt.Client()
client.username_pw_set(username, password)
client.on_message = on_message
client.connect(broker_ip, port)

# Start the MQTT network loop in the background
client.loop_start()

# Subscribe to status topics
client.subscribe(status_topic)
print(f"Subscribed to {status_topic}")

# Flask Slack Command
@bolt_app.command("/doorbell")
def repeat_text(ack, respond, command):
    ack()
    client.publish(topic, "Hello from Python Publisher!")
    print("Message published.")

# Flask Route for Slack Events
@app.route('/slack/events', methods=['POST'])
def slack_events():
    print("Slack event received.")
    return handler.handle(request)

# Run the Flask App
if __name__ == "__main__":
    app.run(port=3000)
