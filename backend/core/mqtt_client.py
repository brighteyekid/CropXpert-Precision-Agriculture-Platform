"""
CropXpert — MQTT subscriber for real-time sensor data ingestion.
Subscribes to cropxpert/farm/+/sensors, parses JSON, stores readings,
triggers ML prediction, and pushes to WebSocket clients.
"""
import json
import logging
import threading
from typing import Callable

import paho.mqtt.client as mqtt
from core.config import get_settings

logger = logging.getLogger("cropxpert.mqtt")
settings = get_settings()

# Connected WebSocket clients — populated by websocket router
ws_clients: set = set()

# Callback set by main.py lifespan to process incoming readings
_on_reading_callback: Callable | None = None


def set_on_reading_callback(cb: Callable):
    global _on_reading_callback
    _on_reading_callback = cb


def _on_connect(client, userdata, flags, rc):
    if rc == 0:
        logger.info("MQTT connected — subscribing to %s", settings.MQTT_TOPIC)
        client.subscribe(settings.MQTT_TOPIC)
    else:
        logger.error("MQTT connection failed — rc=%d", rc)


def _on_message(client, userdata, msg):
    try:
        payload = json.loads(msg.payload.decode())
        # Extract farm_id from topic: cropxpert/farm/<farm_id>/sensors
        parts = msg.topic.split("/")
        farm_id = parts[2] if len(parts) >= 4 else None

        logger.info("MQTT reading from farm %s: %s", farm_id, payload)

        if _on_reading_callback:
            _on_reading_callback(farm_id, payload)

    except json.JSONDecodeError:
        logger.warning("MQTT: invalid JSON on topic %s", msg.topic)
    except Exception as e:
        logger.error("MQTT message processing error: %s", e)


_client: mqtt.Client | None = None


def start_mqtt():
    """Start MQTT subscriber in a background daemon thread."""
    global _client
    _client = mqtt.Client(client_id="cropxpert-backend", protocol=mqtt.MQTTv311)
    _client.on_connect = _on_connect
    _client.on_message = _on_message

    try:
        _client.connect(settings.MQTT_BROKER, settings.MQTT_PORT, keepalive=60)
        thread = threading.Thread(target=_client.loop_forever, daemon=True)
        thread.start()
        logger.info("MQTT subscriber started on %s:%d", settings.MQTT_BROKER, settings.MQTT_PORT)
    except Exception as e:
        logger.warning("MQTT broker unreachable (%s) — running without live sensor feed", e)


def stop_mqtt():
    global _client
    if _client:
        _client.disconnect()
        _client = None
        logger.info("MQTT disconnected")


def publish_reading(farm_id: str | int, data: dict):
    """Publish a sensor reading to MQTT (used when readings come via REST API)."""
    if _client and _client.is_connected():
        topic = f"cropxpert/farm/{farm_id}/sensors"
        _client.publish(topic, json.dumps(data))
