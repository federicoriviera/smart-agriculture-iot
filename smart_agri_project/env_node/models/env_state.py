class EnvState:
    def __init__(
        self,
        battery=100,
        temperature=22.0,
        humidity=60.0,
        wind_speed=5.0,
        is_raining=False,
    ):
        self.battery = battery
        self.temperature = temperature
        self.humidity = humidity
        self.wind_speed = wind_speed
        self.is_raining = is_raining

    def get_battery_level(self):
        return round(self.battery / 100, 2)

    def get_temperature(self):
        return round(self.temperature, 2)

    def get_humidity(self):
        return round(self.humidity, 2)

    def get_wind_speed(self):
        return round(self.wind_speed, 2)
