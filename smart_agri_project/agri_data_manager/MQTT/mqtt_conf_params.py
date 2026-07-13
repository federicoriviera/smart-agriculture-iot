class MqttConfigurationParameters(object):
    BROKER_ADDRESS = "broker.hivemq.com"
    BROKER_PORT = 1883
    MQTT_USERNAME = "progetto_test_agri_12345"
    MQTT_PASSWORD = ""

    DATA_MANAGER_CLIENT_ID = "agri_central_manager"
    MQTT_BASIC_TOPIC = "/iot/user/{0}".format(MQTT_USERNAME)

    NODE_TOPIC = "env_node"
    TELEMETRY_TOPIC = "telemetry"
    ALERT_TOPIC = "alert"

    MAINTENANCE_TOPIC = "maintenance"
    DROUGHT_TOPIC = "drought"
    STORM_TOPIC = "storm"

    RESOLUTION_TOPIC = "res"
    INFO_TOPIC = "info"
    ACTION_TOPIC = "action"
    CONFIG_TOPIC = "config"
