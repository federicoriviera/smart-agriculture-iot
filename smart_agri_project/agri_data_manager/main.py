import time

from models.agri_data_manager import AgriDataManager
from MQTT.agri_manager_mqtt_client import AgriManagerMqttClient
from MQTT.mqtt_conf_params import MqttConfigurationParameters

if __name__ == "__main__":
    # 1. Inizializza il client MQTT del Manager
    data_manager_id = MqttConfigurationParameters.DATA_MANAGER_CLIENT_ID
    mqtt_client = AgriManagerMqttClient(
        data_manager_id,
        MqttConfigurationParameters.BROKER_ADDRESS,
        MqttConfigurationParameters.BROKER_PORT,
    )

    # 2. Inizializza il Manager passandogli il client
    data_manager = AgriDataManager(mqtt_client)

    # 3. Connetti e avvia l'ascolto
    data_manager.mqtt_client.connect()
    data_manager.mqtt_client.loop_start()

    print("Cloud Data Manager Agricolo in ascolto. Premi CTRL+C per fermare.")

    try:
        # Il manager rimane in ascolto infinito dei messaggi dai nodi
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Spegnimento del Cloud Data Manager...")
        data_manager.mqtt_client.loop_stop()
