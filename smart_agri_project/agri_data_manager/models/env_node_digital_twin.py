import time


class EnvNodeDigitalTwin:
    def __init__(self, node_id, descriptor_dict):
        self.node_id = node_id
        self.descriptor = {
            "latitude": descriptor_dict.get("latitude"),
            "longitude": descriptor_dict.get("longitude"),
            "min_humidity_threshold": descriptor_dict.get(
                "min_humidity_threshold", 30.0
            ),
            "max_wind_threshold": descriptor_dict.get("max_wind_threshold", 25.0),
            "battery_threshold": descriptor_dict.get("battery_threshold", 0.2),
        }
        self.last_sync = None
        self.state = {
            "battery": None,
            "temperature": None,
            "humidity": None,
            "wind_speed": None,
            "is_raining": None,
            "irrigation_status": "OFF",
            "rotation_status": "ON",
        }

    def update_state(self, data_dict):
        self.state.update(data_dict)
        self.last_sync = time.time()

    def update_info(self, data_dict):
        self.descriptor.update(data_dict)

    def is_drought(self):
        if self.state["humidity"] is None:
            return False
        return self.state["humidity"] < self.descriptor["min_humidity_threshold"]

    def is_storm(self):
        if self.state["wind_speed"] is None:
            return False
        return self.state["wind_speed"] > self.descriptor["max_wind_threshold"]

    def is_raining(self):
        if self.state["is_raining"] is None:
            return False
        return self.state["is_raining"]

    def is_battery_low(self):
        if self.state["battery"] is None:
            return False
        return self.state["battery"] < self.descriptor["battery_threshold"]
