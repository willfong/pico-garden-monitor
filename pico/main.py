import network
import machine
import time
import urequests
import json
from machine import Pin, ADC, Timer
import dht

try:
    from config import WIFI_SSID, WIFI_PASSWORD, ENDPOINT_URL
except ImportError:
    print("Error: config.py not found. Please create config.py with WIFI_SSID, WIFI_PASSWORD, and ENDPOINT_URL")
    raise

class GardenMonitor:
    def __init__(self):
        self.light_sensor = ADC(Pin(26))  # A0 on Pico W
        self.soil_sensor = ADC(Pin(27))   # A1 on Pico W
        self.dht_sensor = dht.DHT11(Pin(5))  # D5

        self.wifi = network.WLAN(network.STA_IF)
        self.timer = Timer()

        self.connect_wifi()
        self.start_scheduler()

    def connect_wifi(self):
        self.wifi.active(True)
        if not self.wifi.isconnected():
            print(f"Connecting to WiFi: {WIFI_SSID}")
            self.wifi.connect(WIFI_SSID, WIFI_PASSWORD)

            timeout = 0
            while not self.wifi.isconnected() and timeout < 20:
                time.sleep(1)
                timeout += 1
                print(".", end="")

            if self.wifi.isconnected():
                print(f"\nWiFi connected: {self.wifi.ifconfig()}")
            else:
                print("\nFailed to connect to WiFi")
                raise Exception("WiFi connection failed")


    def read_sensors(self):
        try:
            # Read light sensor (0-65535 range)
            light_raw = self.light_sensor.read_u16()
            light_percentage = round((light_raw / 65535) * 100, 2)

            # Read soil moisture (0-65535 range, higher = drier)
            soil_raw = self.soil_sensor.read_u16()
            soil_percentage = round(100 - ((soil_raw / 65535) * 100), 2)  # Invert so higher = wetter

            # Read DHT11 sensor
            self.dht_sensor.measure()
            temperature = self.dht_sensor.temperature()  # Celsius
            humidity = self.dht_sensor.humidity()

            return {
                "light": light_percentage,
                "soil_moisture": soil_percentage,
                "temperature": temperature,
                "humidity": humidity
            }

        except Exception as e:
            print(f"Error reading sensors: {e}")
            return None

    def send_data(self, data):
        try:
            if not self.wifi.isconnected():
                print("WiFi not connected, attempting to reconnect...")
                self.connect_wifi()

            headers = {'Content-Type': 'application/json'}
            response = urequests.post(
                ENDPOINT_URL,
                data=json.dumps(data),
                headers=headers
            )

            if response.status_code == 200:
                print(f"Data sent successfully: {data}")
            else:
                print(f"Failed to send data. Status: {response.status_code}")

            response.close()

        except Exception as e:
            print(f"Error sending data: {e}")

    def sensor_task(self, timer):
        print("Reading sensors...")
        sensor_data = self.read_sensors()

        if sensor_data:
            print(f"Light: {sensor_data['light']}%, Soil: {sensor_data['soil_moisture']}%, Temp: {sensor_data['temperature']}°C, Humidity: {sensor_data['humidity']}%")
            self.send_data(sensor_data)
        else:
            print("Failed to read sensor data")

    def start_scheduler(self):
        # Wait 60 seconds before starting measurements
        print("Waiting 60 seconds before starting measurements...")
        time.sleep(60)

        # Take initial reading
        self.sensor_task(None)

        # Run every 60 seconds (60000 ms) from now on
        self.timer.init(
            period=60000,
            mode=Timer.PERIODIC,
            callback=self.sensor_task
        )
        print("Scheduler started - reading sensors every 60 seconds")

def main():
    try:
        monitor = GardenMonitor()

        # Keep the main thread alive
        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        print("\nShutting down...")
    except Exception as e:
        print(f"Error: {e}")
        machine.reset()

if __name__ == "__main__":
    main()