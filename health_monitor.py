# ---------------------------
# MQTT Subscriber (health_monitor.py)
# ---------------------------
import paho.mqtt.client as mqtt
import json
import pandas as pd
from sklearn.ensemble import IsolationForest

class FootHealthMonitor:
    def __init__(self):
        self.model = IsolationForest(contamination=0.1)
        self.data = pd.DataFrame(columns=[
            'timestamp', 'temp_left', 'temp_right', 
            'pressure_left', 'pressure_right', 'steps', 'pace'
        ])
        
        # MQTT Client setup
        self.client = mqtt.Client(client_id="health_monitor", protocol=mqtt.MQTTv5)
        self.client.tls_set(ca_certs="./certs/ca.crt")
        self.client.username_pw_set("user", "password")
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message

    def on_connect(self, client, userdata, flags, rc):
        client.subscribe("foot/sensors")
        client.subscribe("foot/alerts")

    def on_message(self, client, userdata, msg):
        if msg.topic == "foot/sensors":
            self.process_sensor_data(json.loads(msg.payload))
        elif msg.topic == "foot/alerts":
            print(f"New alert: {msg.payload.decode()}")

    def process_sensor_data(self, data):
        # Add to DataFrame
        new_row = pd.DataFrame([data])
        self.data = pd.concat([self.data, new_row], ignore_index=True)
        
        # Assess health
        status = self.assess_health()
        risks = self.predict_risk()
        
        # Publish alerts
        if status != 'green' or risks:
            alert = {
                'status': status,
                'risks': risks,
                'recommendations': self.generate_recommendations(status, risks)
            }
            self.client.publish("foot/alerts", json.dumps(alert))

    def assess_health(self):
        latest = self.data.iloc[-1]
        temp_diff = abs(latest['temp_left'] - latest['temp_right'])
        
        if temp_diff > 2.2 or latest['pressure_left'] > 300 or latest['pressure_right'] > 300:
            return 'red'
        elif latest['steps'] > 10000:
            return 'yellow'
        return 'green'

    def predict_risk(self):
        # Machine learning prediction
        features = self.data.drop('timestamp', axis=1)
        if len(features) > 10:  # Wait for enough data
            self.model.fit(features)
            return self.model.predict(features[-1:])[0]
        return 0

    def start_monitoring(self):
        self.client.connect("test.mosquitto.org", 8883)
        self.client.loop_forever()

if __name__ == "__main__":
    monitor = FootHealthMonitor()
    monitor.start_monitoring()
