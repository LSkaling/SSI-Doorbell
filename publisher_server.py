from publisher import create_app
from publisher.mqtt import setup_mqtt
from publisher.slack import setup_slack_commands
from publisher.scheduler import start_scheduler
from publisher.database import initialize_database
from publisher.routes import setup_routes

if __name__ == "__main__":
    # Initialize Flask and Slack apps
    flask_app, slack_app, handler = create_app()

    setup_routes(flask_app, handler)

    # Initialize Database
    initialize_database()

    # Setup MQTT
    mqtt_client, node_states = setup_mqtt(slack_app)

    # Setup Slack commands
    slack_channel = "C7F3VVB1S"
    setup_slack_commands(slack_app, mqtt_client, slack_channel)

    # Start scheduler
    start_scheduler(slack_app, slack_channel)

    # Start Flask app
    flask_app.run(port=3000)
