import paho.mqtt.client as mqtt

port = 1883
topic = "test/topic"

client = mqtt.Client()
client.username_pw_set(username, password)
client.connect(broker, port)

client.publish(topic, "Hello from Python Publisher!")
print("Message published.")
