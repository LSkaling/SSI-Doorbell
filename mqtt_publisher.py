import paho.mqtt.client as mqtt

broker = "192.168.1.100"  # Replace with your computer's IP
port = 1883
topic = "test/topic"

client = mqtt.Client()
client.connect(broker, port)

client.publish(topic, "Hello from Python Publisher!")
print("Message published.")
