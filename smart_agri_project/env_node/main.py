import time

from models.env_descriptor import EnvDescriptor
from models.env_node import EnvNode
from models.env_state import EnvState
from MQTT.env_node_mqtt_client import EnvNodeMqttClient
from MQTT.mqtt_conf_params import MqttConfigurationParameters

if __name__ == "__main__":
    node_id = "agri_env_001"
    # Inizializza il descrittore (ID, Lat, Long, Umidità minima %, Vento max km/h, Allarme batteria)
    env_descriptor = EnvDescriptor(node_id, 44.6458, 10.9257, 30.0, 25.0, 0.2)
    env_state = EnvState()

    # Inizializza il client MQTT Reale
    real_mqtt_client = EnvNodeMqttClient(
        node_id,
        MqttConfigurationParameters.BROKER_ADDRESS,
        MqttConfigurationParameters.BROKER_PORT,
    )

    env_node = EnvNode(env_descriptor, env_state, real_mqtt_client)

    env_node.mqtt_client.connect()
    env_node.mqtt_client.loop_start()
    env_node.mqtt_client.publish_info()

    print("Nodo Agricolo avviato. Premi CTRL+C per fermare.")

    # Loop infinito di simulazione del meteo
    i = 0
    try:
        while True:
            env_node.update_measurements()

            # Simuliamo vari eventi atmosferici ciclicamente (ogni 20 iterazioni)
            ciclo = i % 20

            if ciclo == 3:
                env_node.simulate_anomaly("drought")  # Il terreno si secca
                env_node.log_to_file("EVENTO: Inizio siccità simulata.")
            if ciclo == 6:
                env_node.simulate_anomaly("storm")  # Si alza il vento
                env_node.log_to_file("EVENTO: Inizio tempesta di vento simulata.")
            if ciclo == 9:
                env_node.simulate_anomaly("rain_start")  # Inizia a piovere
                env_node.log_to_file("EVENTO: Inizio pioggia simulata.")
            if ciclo == 12:
                env_node.simulate_anomaly_res("rain_stop")  # Smette di piovere
                env_node.log_to_file("EVENTO: Fine pioggia simulata.")

            # Invia i dati al Cloud
            env_node.sync_state_with_cloud()

            print(
                f"Iterazione {i}: Umidità={env_node.state.get_humidity()}%, Vento={env_node.state.get_wind_speed()}km/h, Piove={env_node.state.is_raining}"
            )
            time.sleep(3)  # Pausa tra una lettura e l'altra
            i += 1

    except KeyboardInterrupt:
        print("Spegnimento del Nodo Agricolo...")
        env_node.mqtt_client.loop_stop()
