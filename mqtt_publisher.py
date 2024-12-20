from flask import Flask, request
from slack_bolt import App
from slack_bolt.adapter.flask import SlackRequestHandler
from dotenv import load_dotenv
import os
import paho.mqtt.client as mqtt
from flask import jsonify
import sqlite3
import schedule
import time
from threading import Thread

load_dotenv()

node_states = {}

slack_channel = "C7F3VVB1S"

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

def initialize_database():
    conn = sqlite3.connect('doorbellrings.db')
    with conn:
        cursor = conn.cursor()
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS clients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            client_id TEXT UNIQUE NOT NULL
        )
        ''')

        cursor.execute('''
        CREATE TABLE IF NOT EXISTS invocations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            client_id INTEGER NOT NULL,
            invoked_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (client_id) REFERENCES clients (id) ON DELETE CASCADE
        )
        ''')
    conn.close()

initialize_database()



# MQTT Callbacks
def on_message(client, userdata, message):
    print(f"Status update: {message.topic} -> {message.payload.decode()}")
    # bolt_app.client.chat_postMessage(
    #     channel="C7F3VVB1S",
    #     text=f"Status update: {message.topic} -> {message.payload.decode()}")

    global node_states
    node_id = message.topic.split("/")[-1]  # Extract client_id from "status/<client_id>"
    payload = message.payload.decode()
    print(f"Received message: {payload} on topic {message.topic}")

    # Update the state of the node
    if payload == "online":
        node_states[node_id] = "online"
    elif payload == "offline":
        node_states[node_id] = "offline"    

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

@app.route('/health', methods=['GET'])
def health_check():
    print("Health check received.")
    print(node_states)
    # Check if any node is offline
    if any(state == "offline" for state in node_states.values()):
        return jsonify({
            "node_states": node_states,
            "message": "One or more nodes are offline."
        }), 503  # Return HTTP 503 if a node is offline

    # If all nodes are online
    return jsonify({
        "node_states": node_states,
        "message": "All nodes are online."
    }), 200  # Return HTTP 200 if all nodes are online

def get_db_connection():
    return sqlite3.connect('doorbellrings.db')

def get_or_create_client_id(conn, client_id):
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM clients WHERE client_id = ?", (client_id,))
        row = cursor.fetchone()
        if row is None:
            cursor.execute("INSERT INTO clients (client_id) VALUES (?)", (client_id,))
            conn.commit()
            return cursor.lastrowid
        else:
            return row[0]
    except sqlite3.Error as e:
        print(f"Database error in get_or_create_client_id: {e}")


def record_invocation(client_id):
    conn = get_db_connection()
    try:
        client_internal_id = get_or_create_client_id(conn, client_id)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO invocations (client_id) VALUES (?)", (client_internal_id,))
        conn.commit()
    except sqlite3.Error as e:
        print(f"Database error in record_invocation: {e}")
    finally:
        conn.close()


def get_invocation_counts(days):
    conn = get_db_connection()
    query = """
        SELECT c.client_id, COUNT(i.id) AS invocation_count
        FROM invocations i
        INNER JOIN clients c ON i.client_id = c.id
        WHERE i.invoked_at >= DATETIME('now', ?)
        GROUP BY c.client_id;
    """

    try:
        cursor = conn.cursor()

        # Execute the query with the specified time range
        cursor.execute(query, (f'-{days} days',))

        # Fetch and return the results
        results = cursor.fetchall()
        return results

    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return []

    finally:
        if conn:
            conn.close()    


# Flask Slack Command
@bolt_app.command("/doorbell")
def repeat_text(ack, respond, command):
    ack()
    client.publish(topic, "Hello from Python Publisher!")
    record_invocation(command["user_id"])
    respond(f"Ding dong! The doorbell has been rung")
    print("Message published.")

@bolt_app.command("/doorbell-uses")
def uses(ack, respond, command):
    ack()
    invocations = get_invocation_counts(7)
    print(invocations)

# Flask Route for Slack Events
@app.route('/slack/events', methods=['POST'])
def slack_events():
    print("Slack event received.")
    return handler.handle(request)

def fetch_usage_stats(days):
    conn = get_db_connection()
    query = """
        SELECT c.client_id, COUNT(i.id) AS invocation_count
        FROM invocations i
        INNER JOIN clients c ON i.client_id = c.id
        WHERE i.invoked_at >= DATETIME('now', ?)
        GROUP BY c.client_id;
    """
    try:
        cursor = conn.cursor()
        cursor.execute(query, (f'-{days} days',))
        results = cursor.fetchall()
        return results
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return []
    finally:
        conn.close()

def post_usage_stats():
    try:
        # Fetch stats for the past 14 days
        stats = fetch_usage_stats(14)

        if stats:
            message = "Doorbell usage stats for the past two weeks:\n"
            for client_id, count in stats:
                message += f"- <@{client_id}>: {count} rings\n"
        else:
            message = "No doorbell activity in the past two weeks."

        # Post the message to Slack
        bolt_app.client.chat_postMessage(channel=slack_channel, text=message)
        print("Stats posted to Slack.")
    except Exception as e:
        print(f"Error posting stats to Slack: {e}")

# Schedule the task
#schedule.every(1).minutes.do(post_usage_stats)  # For testing
schedule.every(2).weeks.do(post_usage_stats)  # For production

# Run the scheduler
def run_scheduler():
    while True:
        schedule.run_pending()
        time.sleep(1)

# Run the Flask App
if __name__ == "__main__":
    # Start the Flask app
    flask_thread = Thread(target=lambda: app.run(port=3000))
    flask_thread.daemon = True
    flask_thread.start()

    # Start the scheduler
    run_scheduler()
