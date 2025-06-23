from machine import Pin, ADC, SoftI2C
import network
import dht
import time
import ssd1306
import uasyncio as asyncio
import json
from umqtt.simple import MQTTClient
import time
# Sensor
sensor = dht.DHT11(Pin(4))
adc = ADC(Pin(34))
adc.atten(ADC.ATTN_11DB)
i2c = SoftI2C(sda=Pin(21), scl=Pin(22))
oled = ssd1306.SSD1306_I2C(128, 64, i2c)

# WiFi & MQTT
ssid = 'Nha Tret 2.4G'
password = '01684306403'
mqtt_server = 'broker.hivemq.com'
mqtt_topic = b'esp32/data'
mqtt_client_id = b'esp32-weather'

# Sensor variables
sensor_data = {
    'temp': 0.0,
    'temp_f': 0.0,
    'hum': 0.0,
    'ppm': 0.0
}

# Wifi connection
def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(ssid, password)
    for _ in range(20):
        if wlan.isconnected():
            break
        print(".", end="")
        time.sleep(0.5)
    if wlan.isconnected():
        print("\n✅ WiFi connected:", wlan.ifconfig()[0])
    else:
        print("\n❌ Failed to connect WiFi")
    return wlan

# Sensor read
def read_sensor():
    val = adc.read_u16()
    RS = 10000 * (65536 - val) / val
    ratio = RS / 10000
    ppm = 116.6020682 * (ratio ** -2.769034857)

    for _ in range(3):
        try:
            sensor.measure()
            temp = sensor.temperature()
            hum = sensor.humidity()
            temp_f = temp * 9 / 5 + 32
            return ppm, temp_f, temp, hum
        except OSError:
            print("Retry DHT11...")
            time.sleep(1)
    return ppm, 0.0, 0.0, 0.0

# OLED Display
def show_oled(temp, temp_f, hum, ppm):
    oled.fill(0)
    oled.text(f'Temp C: {temp:.1f}', 0, 0)
    oled.text(f'Temp F: {temp_f:.1f}', 0, 10)
    oled.text(f'Hum: {hum:.1f}%', 0, 20)
    oled.text(f'PPM: {ppm:.1f}', 0, 30)
    oled.show()
def show_loading_screen():
    oled.fill(0)
    oled.text("ESP32 Weather", 10, 10)
    oled.text("Initializing...", 10, 30)
    oled.show()
# Publish data using MQTT protocol 
async def publish_data(client):
    global sensor_data
    while True:
        try:
            ppm, temp_f, temp, hum = read_sensor()
            sensor_data = {
                'temp': temp,
                'temp_f': temp_f,
                'hum': hum,
                'ppm': ppm
            }
            show_oled(temp, temp_f, hum, ppm)
            client.publish(mqtt_topic, json.dumps(sensor_data))
            print("Sent:", sensor_data)
        except Exception as e:
            print("Sensor/MQTT error:", e)
        await asyncio.sleep(5)

# Read HTML and CSS files
def read_file(filename):
    try:
        with open(filename, 'r') as f:
            return f.read()
    except Exception as e:
        print("File lỗi:", e)
        return "<h1>Không đọc được file!</h1>"

# Handle HTML web
async def handle_client(reader, writer): # reader is from client sent and writer is recevied from client
    try:
        req_line = await reader.readline()
        req = req_line.decode().split(" ")[1]
        print("HTTP Request:", req)
        while await reader.readline() != b"\r\n":
            pass
        if req == "/":
            content = read_file("index.html")
            content_type = "text/html"
        elif req == "/style.css":
            content = read_file("style.css")
            content_type = "text/css"
        elif req == "/data": # if the users ask for data from the sensors
            content = json.dumps(sensor_data)
            content_type = "application/json"
        elif req == "/favicon.ico": # handle 404 errors
            content = ""  
            content_type = "image/x-icon"
        else:
            content = "<h1>404 - Not Found</h1>"
            content_type = "text/html"
        await writer.awrite(f"HTTP/1.1 200 OK\r\nContent-Type: {content_type}\r\n\r\n") # HTTP response header 
        await writer.drain()
        await writer.awrite(content)
        await writer.drain()
    except Exception as e:
        print("Web server error:", e)
    finally:
        await writer.aclose()
# Main 
async def main():
    show_loading_screen()
    wlan = connect_wifi()
    if not wlan.isconnected():
        print("Cannot to connnect to Wifi")
        return
    client = MQTTClient(mqtt_client_id, mqtt_server)
    client.connect()
    print("MQTT connected to:", mqtt_server)
    oled.fill(0)
    oled.text("MQTT and Server", 0, 10)
    oled.text("are connected", 5, 30)
    oled.show()
    time.sleep(2)
    asyncio.create_task(publish_data(client))
    server = await asyncio.start_server(handle_client, "0.0.0.0", 80)
    print("Web Server running...")
    await server.wait_closed()

asyncio.run(main())
