import schedule
import time
from threading import Thread
from publisher.database import fetch_usage_stats

def post_usage_stats(slack_app, slack_channel):
    stats = fetch_usage_stats(14)
    message = "Doorbell usage stats for the past two weeks:\n" + "\n".join(
        f"- <@{client_id}>: {count} rings" for client_id, count in stats
    ) if stats else "No doorbell activity in the past two weeks."
    slack_app.client.chat_postMessage(channel=slack_channel, text=message)

def start_scheduler(slack_app, slack_channel):
    schedule.every(2).weeks.do(post_usage_stats, slack_app, slack_channel)

    def run():
        while True:
            schedule.run_pending()
            time.sleep(1)

    Thread(target=run, daemon=True).start()
