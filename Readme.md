# SSI Doorbell

This project allows Slack users to ring a doorbell inside ES3, SSI's workspace. There are two floors, each with a raspberry pi connected to speakers which play a doorbell ring when activated. 

# Status codes
Current status can be viewed at [Uptimebot Status](https://stats.uptimerobot.com/GGkjip9rBK), or at [doorbell.lawtonskaling.com/health](doorbell.lawtonskaling.com/health).

200: Working normally
503: One or more raspberry pi is disconnected
502 / 404: server isn't connecting


# Functionality
- Rings in two locations at once
- Tracks invocations
- Sends a monthly update to workspace-core on stats
- Able to detect when a node goes down and reports that to workspace-core
- Hosted on personal site
- Able to be re-flashed to a new rpi easily

# Implementation
The server is set up using MQTT to manage requests. When the command is invoked in Slack, it sends a POST request to a server running on doorbell.lawtonskaling.com, which is published through MQTT. Raspberry Pis are connected as subscribers to MQTT and play the doorbell audio file when the publisher tells it to. The server is monitored using a Last Will and Testament, and when uptimebot involves the GET request, it returns 200 if all nodes are connected, otherwise an error. 