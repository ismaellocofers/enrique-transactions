import base64
import json
import logging

import sys
from flask import Flask, request, jsonify
from google.cloud import pubsub_v1

from google.cloud import storage




# Configure logging
logging.basicConfig(
    stream=sys.stdout,
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s [%(module)s.%(funcName)s:%(lineno)d] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)



app = Flask(__name__)

@app.route("/", methods=["POST"])
def index():
    
    """Endpoint to receive and process messages."""
    print(request)
    envelope = request.get_json(silent=True)

    print("Mensaje: ",envelope)
    if not envelope or "message" not in envelope:
        return jsonify({"error": "Invalid message format"}), 400

    message = envelope["message"]
    try:
        decoded_message = base64.b64decode(message["data"]).decode("utf-8").strip()
        json_message = json.loads(decoded_message)
        print(json_message.get("concept"))
        publish_response(json_message)
        return jsonify({"status": "success"}), 204
    except Exception as e:
        logging.error(f"Error processing message: {e}")
        return jsonify({"error": "Failed to process message"}), 500




def publish_response(message):
    """Publishes processed message to Pub/Sub topic."""
    publisher = pubsub_v1.PublisherClient()
    topic_path = publisher.topic_path(GCP_PROJECT, OUTPUT_TOPIC)
    message_bytes = json.dumps(message).encode("utf-8")
    publish_future = publisher.publish(topic_path, data=message_bytes)
    publish_future.result()
    logging.info(f"Published message to {topic_path}.")

if __name__ == "__main__":
    app.run(debug=False)