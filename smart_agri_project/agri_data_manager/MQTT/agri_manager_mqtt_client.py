import json
import os
import time

import paho.mqtt.client as mqtt

from .mqtt_conf_params import MqttConfigurationParameters


class AgriManagerMqttClient:
    def __init__(self, client_id, broker_address, broker_port):
        self.manager = None
        self.mqtt_client_id = client_id
        self.broker_address = broker_address
        self.broker_port = broker_port
        self.mqtt_client = mqtt.Client(
            mqtt.CallbackAPIVersion.VERSION1, self.mqtt_client_id, clean_session=False
        )
        self.mqtt_client.username_pw_set(
            MqttConfigurationParameters.MQTT_USERNAME,
            MqttConfigurationParameters.MQTT_PASSWORD,
        )
        self.mqtt_client.on_connect = self.on_connect
        self.mqtt_client.on_message = self.on_message

        self.topic_telemetry = "{0}/{1}/+/{2}".format(
            MqttConfigurationParameters.MQTT_BASIC_TOPIC,
            MqttConfigurationParameters.NODE_TOPIC,
            MqttConfigurationParameters.TELEMETRY_TOPIC,
        )
        self.topic_info = "{0}/{1}/+/{2}".format(
            MqttConfigurationParameters.MQTT_BASIC_TOPIC,
            MqttConfigurationParameters.NODE_TOPIC,
            MqttConfigurationParameters.INFO_TOPIC,
        )

        self.log_filename = os.path.join("..", "logs", "agri_manager_mqtt_log.txt")
        open(self.log_filename, "w").close()

    def log_to_file(self, message):
        timestamp = time.time()
        log_entry = f"timestamp {timestamp}: {message}"
        print(log_entry)
        try:
            with open(self.log_filename, "a") as f:
                f.write(log_entry + "\n")
        except Exception:
            pass

    def set_manager(self, manager):
        self.manager = manager

    def on_connect(self, client, userdata, flags, rc):
        print(f"Connected with id: {self.mqtt_client_id}, with result code: " + str(rc))
        self.mqtt_client.subscribe(self.topic_telemetry, qos=1)
        self.mqtt_client.subscribe(self.topic_info, qos=1)

    def on_message(self, client, userdata, message):
        if self.manager:
            topic = message.topic
            parts = topic.split("/")

            if MqttConfigurationParameters.TELEMETRY_TOPIC in topic:
                senml_payload = json.loads(message.payload.decode())
                node_id = parts[-2]
                data_dict = self.process_senml_to_dict(senml_payload)
                self.manager.process_telemetry(node_id, data_dict)

            if MqttConfigurationParameters.INFO_TOPIC in topic:
                node_id = parts[-2]
                self.manager.process_information_message(
                    node_id, json.loads(message.payload.decode())
                )

    def publish_action(self, node_id, action):
        topic = "{0}/{1}/{2}/{3}".format(
            MqttConfigurationParameters.MQTT_BASIC_TOPIC,
            MqttConfigurationParameters.NODE_TOPIC,
            node_id,
            MqttConfigurationParameters.ACTION_TOPIC,
        )
        payload = json.dumps({"action": action})
        self.mqtt_client.publish(topic, payload, 1)
        self.log_to_file(
            f"agri_manager_mqtt_client: INVIO AZIONE '{action}' AL NODO {node_id}"
        )

    def publish_alert(
        self, node_id, alert_type, alert_id=None, lat=None, lon=None, is_resolved=False
    ):
        topic = "{0}/{1}/{2}/{3}".format(
            MqttConfigurationParameters.MQTT_BASIC_TOPIC,
            MqttConfigurationParameters.ALERT_TOPIC,
            alert_type,
            node_id,
        )
        if is_resolved:
            self.mqtt_client.publish(topic, payload=None, qos=1, retain=True)
        else:
            payload = json.dumps(
                {
                    "node_id": node_id,
                    "alert_id": alert_id,
                    "location": {"lat": lat, "lon": lon},
                    "timestamp": time.time(),
                }
            )
            self.mqtt_client.publish(topic, payload, 1, retain=True)

    def process_senml_to_dict(self, senml_payload):
        data_dict = {}
        data_dict["timestamp"] = senml_payload[0].get("bt", time.time())
        for entry in senml_payload:
            if "n" in entry:
                if "v" in entry:
                    data_dict[entry["n"]] = entry["v"]
                elif "vb" in entry:
                    data_dict[entry["n"]] = entry["vb"]
        return data_dict

    def loop_start(self):
        self.mqtt_client.loop_start()

    def loop_stop(self):
        self.mqtt_client.loop_stop()

    def connect(self):
        self.mqtt_client.connect(self.broker_address, self.broker_port)
