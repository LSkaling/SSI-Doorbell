from flask import request, jsonify
from publisher.mqtt import node_states

def setup_routes(flask_app, handler):
    @flask_app.route('/slack/events', methods=['POST'])
    def slack_events():
        print("Slack event received.")
        return handler.handle(request)
    
    @flask_app.route('/health', methods=['GET'])
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

