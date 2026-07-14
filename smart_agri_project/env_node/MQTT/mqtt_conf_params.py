class MqttConfigurationParameters(object):
    BROKER_ADDRESS = "155.185.4.4"
    BROKER_PORT = 7883
    MQTT_USERNAME = "321408@studenti.unimore.it"
    MQTT_PASSWORD = "mvwjuhqwbkpskocz"

    DATA_MANAGER_CLIENT_ID = "agri_central_manager_321408"
    MQTT_BASIC_TOPIC = "/iot/user/{0}".format(MQTT_USERNAME)

    NODE_TOPIC = "env_node"  # Invece di bin, usiamo env_node
    TELEMETRY_TOPIC = "telemetry"
    ALERT_TOPIC = "alert"

    # Nuovi tipi di allerta agricoli
    MAINTENANCE_TOPIC = "maintenance"
    DROUGHT_TOPIC = "drought"
    STORM_TOPIC = "storm"

    RESOLUTION_TOPIC = "res"
    INFO_TOPIC = "info"
    ACTION_TOPIC = "action"
    CONFIG_TOPIC = "config"
