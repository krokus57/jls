import os
import json
import logging
import paho.mqtt.client as mqtt
from kafka import KafkaProducer
from kafka.errors import NoBrokersAvailable

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# MQTT settings
MQTT_BROKER = os.getenv("MQTT_BROKER", "localhost")
MQTT_PORT = int(os.getenv("MQTT_PORT", 1883))
MQTT_USERNAME = os.getenv("MQTT_USERNAME")
MQTT_PASSWORD = os.getenv("MQTT_PASSWORD")
MQTT_TOPIC = os.getenv("MQTT_TOPIC", "#")

# Kafka settings
KAFKA_BROKER = os.getenv("KAFKA_BROKER", "kafka:9092")
KAFKA_TOPIC = os.getenv("KAFKA_TOPIC", "raw_telemetry")

import time

# Initialize Kafka Producer with retry logic
# Kafka might take a few seconds to start up in docker-compose
producer = None
while producer is None:
    try:
        logger.info(f"Attempting to connect to Kafka at {KAFKA_BROKER}...")
        producer = KafkaProducer(
            bootstrap_servers=[KAFKA_BROKER],
            value_serializer=lambda v: json.dumps(v).encode('utf-8'),
            compression_type='gzip',
            linger_ms=10, # batch small messages slightly
            batch_size=32768
        )
        logger.info("Successfully connected to Kafka!")
    except (Exception, NoBrokersAvailable) as e:
        logger.warning(f"Kafka not ready yet: {e}. Retrying in 5 seconds...")
        time.sleep(5)

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        logger.info(f"Connected to MQTT broker at {MQTT_BROKER}:{MQTT_PORT}")
        client.subscribe(MQTT_TOPIC)
        logger.info(f"Subscribed to topic: {MQTT_TOPIC}")
    else:
        logger.error(f"Failed to connect, return code {rc}")

def on_message(client, userdata, msg):
    payload = msg.payload.decode('utf-8')
    logger.info(f"-> Received message from MQTT topic {msg.topic}: {payload}")
    try:
        # Try to parse as JSON, otherwise keep as raw string
        try:
            data = json.loads(payload)
        except json.JSONDecodeError:
            data = {"value": payload}

        kafka_message = {
            "mqtt_topic": msg.topic,
            "payload": data
        }

        # Send to Kafka
        future = producer.send(KAFKA_TOPIC, kafka_message)
        # Block until sent to ensure delivery and catch errors
        record_metadata = future.get(timeout=10)
        logger.info(f"<- Successfully sent to Kafka partition {record_metadata.partition} at offset {record_metadata.offset}")
    except Exception as e:
        logger.error(f"Error processing/sending message: {e}")

if __name__ == "__main__":
    logger.info("Starting MQTT to Kafka bridge...")

    mqtt_client = mqtt.Client()

    if MQTT_USERNAME and MQTT_PASSWORD:
        mqtt_client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)

    mqtt_client.on_connect = on_connect
    mqtt_client.on_message = on_message

    try:
        mqtt_client.connect(MQTT_BROKER, MQTT_PORT, 60)
        mqtt_client.loop_forever()
    except KeyboardInterrupt:
        logger.info("Shutting down...")
        mqtt_client.disconnect()
        producer.close()
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
