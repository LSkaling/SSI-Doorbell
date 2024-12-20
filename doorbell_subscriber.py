import paho.mqtt.client as mqtt

broker = "192.168.1.100"  # Replace with your computer's IP
port = 1883
topic = "test/topic"

def on_message(client, userdata, msg):
    print(f"Received message: {msg.payload.decode()} on topic {msg.topic}")

client = mqtt.Client()
client.on_message = on_message
client.connect(broker, port)

client.subscribe(topic)
print("Subscribed to topic:", topic)
client.loop_forever()
