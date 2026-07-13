import json
import os
import time

import paho.mqtt.client as mqtt

from .mqtt_conf_params import MqttConfigurationParameters


class EnvNodeMqttClient:
    def __init__(self, node_id, broker_address, broker_port):
        self.manager = None
        self.node_id = node_id
        self.broker_address = broker_address
        self.broker_port = broker_port
        self.mqtt_client_id = node_id
        # Inizializza il client MQTT
        self.mqtt_client = mqtt.Client(
            mqtt.CallbackAPIVersion.VERSION1, self.mqtt_client_id, clean_session=False
        )
        self.mqtt_client.username_pw_set(
            MqttConfigurationParameters.MQTT_USERNAME,
            MqttConfigurationParameters.MQTT_PASSWORD,
        )
        self.mqtt_client.on_connect = self.on_connect
        self.mqtt_client.on_message = self.on_message

        # Definizione dei Topic
        self.topic_telemetry = "{0}/{1}/{2}/{3}".format(
            MqttConfigurationParameters.MQTT_BASIC_TOPIC,
            MqttConfigurationParameters.NODE_TOPIC,
            self.node_id,
            MqttConfigurationParameters.TELEMETRY_TOPIC,
        )

        self.topic_action = "{0}/{1}/{2}/{3}".format(
            MqttConfigurationParameters.MQTT_BASIC_TOPIC,
            MqttConfigurationParameters.NODE_TOPIC,
            self.node_id,
            MqttConfigurationParameters.ACTION_TOPIC,
        )

        self.topic_config = "{0}/{1}/{2}/{3}".format(
            MqttConfigurationParameters.MQTT_BASIC_TOPIC,
            MqttConfigurationParameters.NODE_TOPIC,
            self.node_id,
            MqttConfigurationParameters.CONFIG_TOPIC,
        )

        self.topic_info = "{0}/{1}/{2}/{3}".format(
            MqttConfigurationParameters.MQTT_BASIC_TOPIC,
            MqttConfigurationParameters.NODE_TOPIC,
            self.node_id,
            MqttConfigurationParameters.INFO_TOPIC,
        )

        self.log_filename = os.path.join("..", "logs", "env_node_mqtt_client_log.txt")
        os.makedirs(os.path.dirname(self.log_filename), exist_ok=True)
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
        print(f"Connected with id: {self.mqtt_client_id}, result code: " + str(rc))
        # Si iscrive per ricevere comandi (azioni) e configurazioni dal Cloud
        self.mqtt_client.subscribe(self.topic_action, qos=1)
        self.mqtt_client.subscribe(self.topic_config, qos=1)

    def on_message(self, client, userdata, message):
        if self.manager:
            topic = message.topic
            try:
                message_payload = json.loads(message.payload.decode())
                if MqttConfigurationParameters.ACTION_TOPIC in topic:
                    self.log_to_file(
                        f"env_node_mqtt_client; azione ricevuta: {message_payload}"
                    )
                    if hasattr(self.manager, "action_received"):
                        self.manager.action_received(message_payload.get("action"))

                if MqttConfigurationParameters.CONFIG_TOPIC in topic:
                    self.log_to_file(
                        f"env_node_mqtt_client; configurazione ricevuta: {message_payload}"
                    )
                    self.manager.config_received(message_payload.get("config"))
            except Exception as e:
                self.log_to_file(f"Errore parsing messaggio: {e}")

    def publish_telemetry(self):
        if self.manager:
            payload = self.format_senml_telemetry_payload()
            self.mqtt_client.publish(self.topic_telemetry, payload, qos=1)
            self.log_to_file(f"env_node_mqtt_client; telemetria pubblicata: {payload}")

    def format_senml_telemetry_payload(self):
        node_id = self.manager.descriptor.node_id
        state = self.manager.state

        # Crea il pacchetto in formato SenML con tutti i dati ambientali
        senml_payload = [
            {"bn": f"{node_id}/", "bt": round(time.time(), 2)},
            {"n": "battery", "u": "/", "v": state.get_battery_level()},
            {"n": "temperature", "u": "Cel", "v": state.get_temperature()},
            {"n": "humidity", "u": "%RH", "v": state.get_humidity()},
            {"n": "wind_speed", "u": "km/h", "v": state.get_wind_speed()},
            {"n": "is_raining", "vb": state.is_raining},
        ]
        return json.dumps(senml_payload)

    def publish_info(self):
        if self.manager:
            payload = self.manager.descriptor.to_json()
            self.mqtt_client.publish(self.topic_info, payload, qos=1, retain=True)
            self.log_to_file(f"env_node_mqtt_client; info pubblicate: {payload}")

    def connect(self):
        self.mqtt_client.connect(self.broker_address, self.broker_port)

    def loop_start(self):
        self.mqtt_client.loop_start()

    def loop_stop(self):
        self.mqtt_client.loop_stop()
