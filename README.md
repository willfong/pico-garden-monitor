# 🌱 Pico Garden Monitor

A comprehensive garden monitoring system using Raspberry Pi Pico W with sensors for soil moisture, light, temperature, and humidity. Includes a web dashboard for real-time monitoring and historical data visualization.

## 📋 Hardware Requirements

### Raspberry Pi Pico W Setup
- [Cytron Maker Pi Pico Mini](https://sg.cytron.io/c-raspberry-pi/p-maker-pi-pico-mini-simplifying-projects-with-raspberry-pi-pico)
- [Grove Light Sensor v1.2](https://sg.cytron.io/p-grove-light-sensor-v1.2)
- [Grove Temperature and Humidity Sensor DHT11](https://sg.cytron.io/p-grove-temperature-and-humidity-sensor-dht11)
- [Maker Soil Moisture Sensor](https://sg.cytron.io/p-maker-soil-moisture-sensor)

### Wiring Connections
- **Light Sensor**: Pin A0 (GPIO 26)
- **Soil Moisture Sensor**: Pin A1 (GPIO 27)
- **DHT11 Temperature/Humidity Sensor**: Pin D5 (GPIO 5)

## 🚀 Quick Start

### 1. Pico W Setup (MicroPython)

1. **Install MicroPython** on your Pico W following the [official guide](https://www.raspberrypi.org/documentation/microcontrollers/micropython.html)

2. **Copy configuration file**:
   ```bash
   cd pico/
   cp config.py.example config.py
   ```

3. **Edit configuration**:
   ```python
   # config.py
   WIFI_SSID = "your_wifi_network_name"
   WIFI_PASSWORD = "your_wifi_password"
   ENDPOINT_URL = "http://192.168.1.100:5000/api/sensor-data"  # Replace with your server IP
   TIMEZONE_OFFSET = 8  # Timezone offset from UTC in hours (e.g., +8 for Singapore, -5 for EST)
   ```

4. **Upload files to Pico W**:
   - Copy `main.py` and `config.py` to your Pico W using one of the following methods:
     - **Thonny IDE**: Open files and save them directly to the Pico W
     - **rshell**: Command-line tool for MicroPython file management
     - **From Raspberry Pi**: Use `rshell` or `mpremote` (see section below)

5. **Run the sensor script**:
   - The script will automatically start when the Pico W boots
   - It will connect to WiFi and begin sending sensor data every 60 seconds

### 2. Server Setup (Python/Flask)

1. **Install Python dependencies**:
   ```bash
   cd server/
   pip install -r requirements.txt
   ```

2. **Run the server**:
   ```bash
   python app.py
   ```

3. **Access the dashboard**:
   - Open your browser to `http://localhost:5000`
   - The dashboard will show real-time sensor data and historical charts

## 📊 Features

### Pico W Sensor Script
- **WiFi Connectivity**: Automatic connection with retry logic
- **Precise Timing**: Uses Timer interrupt to read sensors every 60 seconds (no drift)
- **Multiple Sensors**:
  - Light level (0-100%)
  - Soil moisture (0-100%, where higher = wetter)
  - Temperature (Celsius)
  - Air humidity (0-100%)
- **HTTP Data Transmission**: JSON payload sent to Flask server
- **Error Handling**: Graceful handling of sensor failures and network issues

### Web Dashboard
- **Responsive Design**: Mobile-friendly using Tailwind CSS
- **Real-time Monitoring**: Current sensor values displayed in cards
- **Historical Charts**: 3-day trend graphs using Chart.js
- **Recent Data Table**: Detailed minute-by-minute readings for the past hour
- **Auto-refresh**: Dashboard updates every 30 seconds

### Database
- **SQLite Storage**: All sensor data stored locally
- **Data Aggregation**: Chart data averaged by minute for better visualization
- **API Endpoints**: RESTful API for data access

## 🛠️ Configuration

### Sensor Calibration

The sensor readings are processed as follows:

- **Light Sensor**: Raw ADC value (0-65535) converted to percentage (0-100%)
- **Soil Moisture**: Raw ADC value inverted so higher values indicate wetter soil
- **DHT11**: Direct temperature (°C) and humidity (%) readings

### Timezone Configuration

The system handles timezones properly:

- **Pico W**: Sends both UTC and local timestamps based on `TIMEZONE_OFFSET` setting
- **Server**: Stores timezone-aware timestamps for accurate data handling
- **Dashboard**: Automatically displays all times in the user's browser timezone
- **Data Consistency**: All historical data maintains proper timezone information

### Server Configuration

The Flask server runs on all interfaces (`0.0.0.0`) on port 5000 by default. To change:

```python
# In app.py, modify the last line:
app.run(host='0.0.0.0', port=YOUR_PORT, debug=False)
```

### Copying Files from Raspberry Pi to Pico W

If you're deploying from a Raspberry Pi, you can use these methods to transfer files to your Pico W:

#### Method 1: Using mpremote (Recommended)

1. **Install mpremote**:
   ```bash
   pip install mpremote
   ```

2. **Connect Pico W via USB** to your Raspberry Pi

3. **Copy files**:
   ```bash
   # Navigate to the pico directory
   cd pico/

   # Copy main.py to the Pico W
   mpremote cp main.py :main.py

   # Copy your config.py to the Pico W
   mpremote cp config.py :config.py

   # Verify files were copied
   mpremote ls
   ```

4. **Reset the Pico W** to start the new code:
   ```bash
   mpremote reset
   ```

#### Method 2: Using rshell

1. **Install rshell**:
   ```bash
   pip install rshell
   ```

2. **Connect to Pico W**:
   ```bash
   rshell -p /dev/ttyACM0
   ```

3. **Copy files** (within rshell):
   ```bash
   cp main.py /pyboard/
   cp config.py /pyboard/
   ls /pyboard/
   ```

4. **Exit rshell and reset**:
   ```bash
   exit
   mpremote reset
   ```

#### Finding the Correct Serial Port

If `/dev/ttyACM0` doesn't work, find the correct port:
```bash
# List USB devices
lsusb | grep -i pico

# List serial devices
ls /dev/tty*

# Usually it's one of:
# /dev/ttyACM0, /dev/ttyACM1, /dev/ttyUSB0, etc.
```

## 📡 API Endpoints

### POST `/api/sensor-data`
Receives sensor data from Pico W.

**Request Body**:
```json
{
  "light": 75.5,
  "soil_moisture": 45.2,
  "temperature": 24.5,
  "humidity": 60.8,
  "timestamp": 1704067200
}
```

### GET `/api/data/recent`
Returns sensor readings from the past hour.

### GET `/api/data/chart`
Returns aggregated data for the past 3 days (averaged by minute).

## 🔧 Troubleshooting

### Pico W Issues

**WiFi Connection Problems**:
- Verify SSID and password in `config.py`
- Check that your router supports 2.4GHz (Pico W doesn't support 5GHz)
- Ensure the Pico W is within range of your WiFi router

**Sensor Reading Issues**:
- Verify wiring connections
- Check that sensors are properly powered
- Monitor serial output for error messages

**Network Issues**:
- Verify the server IP address in `config.py`
- Ensure the server is running and accessible
- Check firewall settings

### Server Issues

**Database Problems**:
- The SQLite database is created automatically
- Check file permissions in the server directory
- Verify Python has write access to the directory

**Dashboard Not Loading**:
- Check that Flask is running on the correct port
- Verify all template files are in the `templates/` directory
- Check browser console for JavaScript errors

## 📁 Project Structure

```
pico-garden-monitor/
├── pico/                          # Pico W MicroPython code
│   ├── main.py                    # Main sensor script
│   └── config.py.example          # Configuration template
├── server/                        # Flask web server
│   ├── app.py                     # Main Flask application
│   ├── requirements.txt           # Python dependencies
│   └── templates/
│       └── dashboard.html         # Web dashboard
└── README.md                      # This file
```

## 🔮 Future Enhancements

- [ ] Add email/SMS alerts for extreme conditions
- [ ] Implement data export functionality (CSV, JSON)
- [ ] Add more sensor types (pH, light spectrum, etc.)
- [ ] Create mobile app companion
- [ ] Add automated watering system integration
- [ ] Historical data analysis and predictions

## 📄 License

This project is open source and available under the MIT License.

## 🤝 Contributing

Feel free to submit issues, feature requests, and pull requests to improve this garden monitoring system!

---

Happy Gardening! 🌱