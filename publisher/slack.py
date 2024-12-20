from publisher.database import record_invocation, fetch_usage_stats

def setup_slack_commands(slack_app, mqtt_client, slack_channel):
    @slack_app.command("/doorbell2")
    def ring_doorbell(ack, respond, command):
        ack()
        mqtt_client.publish("test/topic", "Hello from Python Publisher!")
        record_invocation(command["user_id"])
        respond("Ding dong! The doorbell has been rung!")
        print("Message published.")

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
