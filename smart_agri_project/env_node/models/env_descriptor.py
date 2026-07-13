import json


class EnvDescriptor:
    def __init__(
        self,
        node_id,
        latitude,
        longitude,
        min_humidity_threshold=30.0,
        max_wind_threshold=25.0,
        battery_threshold=0.2,
    ):
        self.node_id = node_id
        self.latitude = latitude
        self.longitude = longitude
        self.min_humidity_threshold = min_humidity_threshold
        self.max_wind_threshold = max_wind_threshold
        self.battery_threshold = battery_threshold

    def to_json(self):
        return json.dumps(self.__dict__)
