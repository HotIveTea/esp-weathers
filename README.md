# Esp32 Weather Station
## ESP32 Weather Station with OLED, MQTT, and Web Dashboard
### Objective
### This project implements a compact weather station using an ESP32 microcontroller that:
- Reads data from DHT11 (temperature & humidity) and MQ135 (air quality) sensors.
- Displays live sensor data on an OLED screen (SSD1306).
- Publishes the data to an MQTT broker in JSON format.
- Hosts a local web server on the ESP32 to serve an HTML dashboard.
- Allows remote real-time visualization via a GitHub Pages-hosted front-end.

## Hardware Components
### Component	Description
- ESP32 Dev Board	Main microcontroller
- DHT11	Measures temperature and humidity
- MQ135	Measures air quality (PPM)
- SSD1306 OLED	Displays sensor data
## Pin Connections
- Sensor/Module	ESP32 GPIO Pin
- DHT11	GPIO4
- MQ135 (Analog) + GPIO34 (ADC1)
- OLED SDA	GPIO21
- OLED SCL	GPIO22

## Key Functionalities
### 1. Sensor Reading
Reads temperature and humidity using the dht.DHT11 module.
Calculates PPM from MQ135 using ADC and resistance ratio formula: (this maybe wrong, if you have a better fomula just use it)
```python
RS = 10k * (65536 - value) / value
PPM = 116.6020682 * (RS/R0)^-2.769034857
```
### 2. OLED Display
Continuously displays:
- Temperature (Celsius and Fahrenheit)
- Humidity (%)
- Air Quality (PPM)
### 3. MQTT Communication
- Uses the umqtt.simple library for publishing.
- Sends sensor data as JSON every 5 seconds.
- Tested on public brokers like: broker.hivemq.com or test.mosquitto.org

Example payload:
```python
{
  "temp": 28.5,
  "temp_f": 83.3,
  "hum": 75.0,
  "ppm": 310.2
}
```
### 4. Local HTTP Server on ESP32
A simple web server using uasyncio listens on port 80.
Endpoints:
- / → serves index.html
- /style.css → serves CSS file
- /data → returns JSON of latest sensor data
### 5. Remote Web Dashboard
- Front-end built with HTML, CSS, Chart.js, and MQTT.js (WebSocket).
- Real-time graphs of temperature, humidity, and air quality.
- Forecast logic based on sensor readings.
- Can be hosted on GitHub Pages for global access.

### How to Host on GitHub Pages
- Create a new public repository.
- Upload index.html and style.css.
- Go to Settings > Pages > Select branch main, folder /root.
The dashboard is now accessible at: https://<your-username>.github.io/<repo-name>/
### Technologies and Skills Learned
- MicroPython
- machine.Pin, ADC, SoftI2C
- uasyncio for running tasks concurrently
- File handling (open(), read())
- OLED control with ssd1306
- Communication Protocols:
  - HTTP: Local server with custom HTML/CSS responses
  - MQTT: Publish-subscribe pattern for data communication
- JSON: Structured data formatting and transmission
- WebSocket (via MQTT.js): Real-time dashboard integration
- Chart.js for data visualization ( stolen from internet)
- MQTT.js for WebSocket-based broker connection
### Some images about the project
![alt text]("C:\Users\Admin\Downloads\z6739964476523_3ff79049ff001856ac2eccd038b6a261.jpg")
![alt text]("C:\Users\Admin\Pictures\Screenshots\Screenshot 2025-06-25 105555.png")
### Possible Extensions
- Add buzzer alerts for poor air quality
- Save data to Firebase or Google Sheets
- Use a larger display or mobile notification system
- Apply basic AI logic for smarter forecasting (Definitely work in the future)
### License
This project was developed for educational purposes using ESP32, MicroPython, and MQTT technologies.
