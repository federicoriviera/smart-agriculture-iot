import os
import time

from models.alert import Alert
from models.env_node_digital_twin import EnvNodeDigitalTwin
from MQTT.mqtt_conf_params import MqttConfigurationParameters


class AgriDataManager:
    def __init__(self, mqtt_client):
        self.mqtt_client = mqtt_client
        self.active_nodes = {}
        self.mqtt_client.set_manager(self)
        self.active_alerts = {
            MqttConfigurationParameters.DROUGHT_TOPIC: {},
            MqttConfigurationParameters.MAINTENANCE_TOPIC: {},
            MqttConfigurationParameters.STORM_TOPIC: {},
        }
        self.alert_id = 0

        self.log_filename = os.path.join("..", "logs", "agri_data_manager_log.txt")
        os.makedirs(os.path.dirname(self.log_filename), exist_ok=True)
        open(self.log_filename, "w").close()
        self.log_to_file("Log del Data Manager pulito e avviato.")

    def log_to_file(self, message):
        timestamp = time.time()
        log_entry = f"timestamp {timestamp}: {message}"
        print(log_entry)
        try:
            with open(self.log_filename, "a") as f:
                f.write(log_entry + "\n")
        except Exception as e:
            print(f"Errore durante la scrittura del log: {e}")

    def process_telemetry(self, node_id, data_dict):
        if node_id not in self.active_nodes:
            return

        # Rimuoviamo la chiave dal dizionario ma senza assegnarla a una variabile inutilizzata
        data_dict.pop("timestamp", None)

        target_node = self.active_nodes[node_id]
        target_node.update_state(data_dict)

        # Esegui i controlli ambientali ogni volta che arriva un dato
        self.perform_checks(node_id)

    def process_information_message(self, node_id, info_dict):
        if node_id not in self.active_nodes:
            if node_id == info_dict.get("node_id"):
                self.active_nodes[node_id] = EnvNodeDigitalTwin(
                    node_id=node_id, descriptor_dict=info_dict
                )
                self.log_to_file(
                    f"agri_data_manager; Nuovo nodo agricolo registrato: {node_id}"
                )
        else:
            if node_id == info_dict.get("node_id"):
                self.active_nodes[node_id].update_info(info_dict)

    def generate_alert(self, target_node, alert_type):
        if (
            target_node.node_id not in self.active_alerts[alert_type]
            or self.active_alerts[alert_type][target_node.node_id].resolved
        ):
            alert = Alert(target_node.node_id, self.alert_id, alert_type)
            self.alert_id += 1
            self.active_alerts[alert_type][target_node.node_id] = alert
            self.mqtt_client.publish_alert(
                target_node.node_id,
                alert_type,
                alert.alert_id,
                target_node.descriptor["latitude"],
                target_node.descriptor["longitude"],
            )
            self.log_to_file(
                f"agri_data_manager; GENERATO ALLARME {alert_type} per il nodo {target_node.node_id}"
            )

    def resolve_alert(self, target_node, alert_type):
        if target_node.node_id in self.active_alerts[alert_type]:
            self.active_alerts[alert_type].pop(target_node.node_id, None)
            self.mqtt_client.publish_alert(
                target_node.node_id, alert_type, is_resolved=True
            )
            self.log_to_file(
                f"agri_data_manager; Allarme {alert_type} per {target_node.node_id} RISOLTO in automatico"
            )

    def perform_checks(self, node_id):
        if node_id in self.active_nodes:
            target_node = self.active_nodes[node_id]

            # --- LOGICA 1: GESTIONE PIOGGIA E SICCITA' ---
            if target_node.is_raining():
                # Se piove, spegniamo subito l'irrigazione e risolviamo eventuale allarme siccità
                if target_node.state["irrigation_status"] != "OFF":
                    self.mqtt_client.publish_action(node_id, "irrigation_off")
                    target_node.state["irrigation_status"] = "OFF"
                self.resolve_alert(
                    target_node, MqttConfigurationParameters.DROUGHT_TOPIC
                )

            elif target_node.is_drought():
                # Se non piove ed è secco, accendiamo l'irrigazione
                if target_node.state["irrigation_status"] != "ON":
                    self.mqtt_client.publish_action(node_id, "irrigation_on")
                    target_node.state["irrigation_status"] = "ON"
                self.generate_alert(
                    target_node, MqttConfigurationParameters.DROUGHT_TOPIC
                )
            else:
                self.resolve_alert(
                    target_node, MqttConfigurationParameters.DROUGHT_TOPIC
                )

            # --- LOGICA 2: GESTIONE VENTO ---
            if target_node.is_storm():
                # Se c'è troppo vento, fermiamo la rotazione dell'irrigatore
                if target_node.state["rotation_status"] != "OFF":
                    self.mqtt_client.publish_action(node_id, "rotation_off")
                    target_node.state["rotation_status"] = "OFF"
                self.generate_alert(
                    target_node, MqttConfigurationParameters.STORM_TOPIC
                )
            else:
                if target_node.state["rotation_status"] != "ON":
                    self.mqtt_client.publish_action(node_id, "rotation_on")
                    target_node.state["rotation_status"] = "ON"
                self.resolve_alert(target_node, MqttConfigurationParameters.STORM_TOPIC)

            # --- LOGICA 3: GESTIONE BATTERIA ---
            if target_node.is_battery_low():
                self.generate_alert(
                    target_node, MqttConfigurationParameters.MAINTENANCE_TOPIC
                )
            else:
                self.resolve_alert(
                    target_node, MqttConfigurationParameters.MAINTENANCE_TOPIC
                )
