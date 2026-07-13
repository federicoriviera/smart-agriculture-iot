class DataManagerConfigParameters(object):
    # Soglia di umidità sotto la quale si considera "Siccità" e si attiva l'irrigazione
    MIN_HUMIDITY_THRESHOLD = 30.0
    # Soglia di vento sopra la quale si disattiva la rotazione per non disperdere acqua
    MAX_WIND_THRESHOLD = 25.0
    # Soglia batteria (20%)
    BATTERY_THRESHOLD = 0.2
