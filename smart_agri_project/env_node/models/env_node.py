import os
import random
import time


class EnvNode:
    def __init__(self, descriptor, state, mqtt_client):
        self.descriptor = descriptor
        self.state = state
        self.mqtt_client = mqtt_client
        self.mqtt_client.set_manager(self)

        # Assicurati che la cartella logs esista al livello superiore
        self.log_filename = os.path.join("..", "logs", "env_node_log.txt")
        os.makedirs(os.path.dirname(self.log_filename), exist_ok=True)
        open(self.log_filename, "w").close()
        self.log_to_file("Log del nodo ambientale inizializzato.")

    def log_to_file(self, message):
        timestamp = time.time()
        log_entry = f"timestamp {timestamp}: {message}"
        print(log_entry)
        try:
            with open(self.log_filename, "a") as f:
                f.write(log_entry + "\n")
        except Exception as e:
            print(f"Errore durante la scrittura del log: {e}")

    # Ricezione comandi di attuazione dal Cloud
    def action_received(self, action):
        self.log_to_file(f"env_node; azione ricevuta dal Cloud: {action}")
        if action == "irrigation_on":
            self.log_to_file("-> ATTUATORE: Irrigazione ACCESA")
        elif action == "irrigation_off":
            self.log_to_file("-> ATTUATORE: Irrigazione SPENTA")
        elif action == "rotation_on":
            self.log_to_file("-> ATTUATORE: Rotazione irrigatore ACCESA")
        elif action == "rotation_off":
            self.log_to_file("-> ATTUATORE: Rotazione irrigatore SPENTA")

    # Ricezione di nuove configurazioni dal Cloud (es. cambio coltura)
    def config_received(self, config_dictionary):
        self.log_to_file(
            f"env_node; nuova configurazione ricevuta: {config_dictionary}"
        )
        if "min_humidity_threshold" in config_dictionary:
            self.descriptor.min_humidity_threshold = config_dictionary[
                "min_humidity_threshold"
            ]
            self.log_to_file(
                f"env_node; nuova soglia umidità minima impostata: {self.descriptor.min_humidity_threshold}"
            )
        if "max_wind_threshold" in config_dictionary:
            self.descriptor.max_wind_threshold = config_dictionary["max_wind_threshold"]
            self.log_to_file(
                f"env_node; nuova soglia vento massimo impostata: {self.descriptor.max_wind_threshold}"
            )

    def sync_state_with_cloud(self):
        self.mqtt_client.publish_telemetry()

    # Simula il passare del tempo e il cambiamento del meteo
    def update_measurements(self):
        if self.state.battery > 0:
            # La batteria scende lentamente
            self.state.battery = round(
                max(0, self.state.battery - random.uniform(0.1, 0.5)), 2
            )

            # La temperatura varia leggermente
            self.state.temperature = round(
                self.state.temperature + random.uniform(-0.5, 0.5), 2
            )

            # Se non piove, il terreno si asciuga lentamente (umidità scende)
            if not self.state.is_raining:
                self.state.humidity = round(
                    max(0, self.state.humidity - random.uniform(1.0, 3.0)), 2
                )
            else:
                # Se piove, l'umidità sale rapidamente
                self.state.humidity = round(
                    min(100, self.state.humidity + random.uniform(5.0, 10.0)), 2
                )

            # Il vento varia
            self.state.wind_speed = round(
                max(0, self.state.wind_speed + random.uniform(-2.0, 3.0)), 2
            )

    # Permette di simulare eventi atmosferici estremi da testare
    def simulate_anomaly(self, anomaly):
        if anomaly == "drought":  # Siccità
            self.state.humidity = 10.0
        elif anomaly == "storm":  # Tempesta (vento forte)
            self.state.wind_speed = 35.0
        elif anomaly == "rain_start":  # Inizia a piovere
            self.state.is_raining = True
        elif anomaly == "battery_low":
            self.state.battery = 5.0

    def simulate_anomaly_res(self, anomaly):
        if anomaly == "drought":
            self.state.humidity = 60.0
        elif anomaly == "storm":
            self.state.wind_speed = 5.0
        elif anomaly == "rain_stop":
            self.state.is_raining = False
        elif anomaly == "battery":
            self.state.battery = 100.0
