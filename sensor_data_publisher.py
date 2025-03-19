# ---------------------------
# MQTT Publisher (sensor_data_publisher.py)
# ---------------------------
import pandas as pd
import paho.mqtt.client as mqtt
import json
import time

class SensorDataPublisher:
    def __init__(self):
        self.client = mqtt.Client(client_id="foot_sensor_publisher", protocol=mqtt.MQTTv5)
        self.client.tls_set(ca_certs="./certs/ca.crt")  # For TLS encryption
        self.client.username_pw_set("user", "password")
        self.client.connect("test.mosquitto.org", 8883)  # Public test broker

    def publish_csv_data(self, csv_path="foot_sensor_data.csv"):
        df = pd.read_csv(csv_path)
        for _, row in df.iterrows():
            payload = {
                'timestamp': row['timestamp'],
                'temp_left': row['temp_left'],
                'temp_right': row['temp_right'],
                'pressure_left': row['pressure_left'],
                'pressure_right': row['pressure_right'],
                'steps': row['steps'],
                'pace': row['pace']
            }
            self.client.publish("foot/sensors", json.dumps(payload))
            time.sleep(1)  # Simulate real-time data flow

if __name__ == "__main__":
    publisher = SensorDataPublisher()
    publisher.publish_csv_data()
