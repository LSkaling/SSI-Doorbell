from publisher.database import record_invocation, fetch_usage_stats
from publisher.mqtt import node_states


def setup_slack_commands(slack_app, mqtt_client, slack_channel):
    @slack_app.command("/doorbell")
    def ring_doorbell(ack, respond, command):
        ack()
        mqtt_client.publish("test/topic", "Hello from Python Publisher!")
        print("Message published.")
        respond("Ding dong! The doorbell has been rung!")
        if all(state == "online" for state in node_states.values()):
            respond("Ding dong! The doorbell has been rung!")
        elif any(state == "offline" for state in node_states.values()):
            respond("Ding dong darn! The doorbell has been rung, but some nodes are offline. Server maintainers have been notified, you can check the status here: https://stats.uptimerobot.com/GGkjip9rBK/798229249")
        else:
            respond("Ding dong darn! The doorbell is offline! Server maintainers have been notified, you can check the status here: https://stats.uptimerobot.com/GGkjip9rBK/798229249")
        record_invocation(command["user_id"])

    @slack_app.command("/doorbell-uses")
    def usage_stats(ack, respond, command):
        ack()
        stats = fetch_usage_stats(7)
        if stats:
            message = "Doorbell usage stats:\n" + "\n".join(
                f"- <@{client_id}>: {count} rings" for client_id, count in stats
            )
        else:
            message = "No doorbell activity in the past 7 days."
        respond(message)
