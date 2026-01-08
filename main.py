import time
time.sleep(3)  # 🔑 BOOT SAFETY: allows Thonny to interrupt

from machine import Pin, RTC, PWM
import network
import ntptime

from sensors import DHTSensor
from display import OLEDDisplay
from server import HTTPServer
from ota import OTAUpdater
from heater_control import HeaterController

# ====================
# WIFI CONFIG
# ====================
WIFI_SSID = "APT3-23-24"
WIFI_PASSWORD = "12345#23WorcesterSq#"
SENSOR_UPDATE_INTERVAL = 2

# ====================
# HARDWARE SETUP
# ====================
sensor = DHTSensor(15)
oled = OLEDDisplay()
server = HTTPServer()
heater = HeaterController()
rtc = RTC()

# ====================
# GLOBAL STATE
# ====================
device_ip = None
last_temp_c = None
last_temp_f = None
last_humidity = None
last_update = 0

# ====================
# WIFI CONNECT
# ====================
def connect_wifi():
    global device_ip
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(WIFI_SSID, WIFI_PASSWORD)

    oled.show_message("Connecting WiFi")

    timeout = 20
    while not wlan.isconnected() and timeout > 0:
        time.sleep(1)
        timeout -= 1

    if not wlan.isconnected():
        raise RuntimeError("WiFi failed")

    device_ip = wlan.ifconfig()[0]
    oled.show_message("WiFi Connected", device_ip)

# ====================
# TIME SYNC
# ====================
def sync_time_on_boot():
    oled.show_message("Syncing Time...")

    for _ in range(5):
        try:
            ntptime.settime()  # UTC
            return
        except:
            time.sleep(2)

def get_local_time():
    _, _, _, hour, minute, _, _, _ = time.localtime()
    hour = (hour - 5) % 24  # EST offset

    if hour == 0:
        h, ap = 12, "AM"
    elif hour < 12:
        h, ap = hour, "AM"
    elif hour == 12:
        h, ap = 12, "PM"
    else:
        h, ap = hour - 12, "PM"

    return "{:2d}:{:02d} {}".format(h, minute, ap)

# ====================
# SENSOR + OLED + LED
# ====================
def update_sensor_and_oled():
    global last_temp_c, last_temp_f, last_humidity, last_update

    if time.time() - last_update < SENSOR_UPDATE_INTERVAL:
        return
    
    temp_c, temp_f, humidity = sensor.read()
    if temp_c is None:
        return

    last_temp_c = temp_c
    last_temp_f = temp_f
    last_humidity = humidity
    last_update = time.time()

    oled.show_reading(get_local_time(), last_temp_c, last_humidity)
    server.update_readings(last_temp_c, last_temp_f, last_humidity)

    # Check temperature and control heater
    heater.check_and_control(last_temp_c)

# ====================
# MAIN
# ====================
try:
    time.sleep(2)
    ota = OTAUpdater()
    has_update, version, payload = ota.check_for_update()

    if has_update:
        oled.show_message("Updating...", "Please wait")
        files, base_url = payload
        ota.install_update(files, base_url)

    # ---- NORMAL STARTUP ----
    connect_wifi()
    sync_time_on_boot()
    update_sensor_and_oled()
    server.start(update_sensor_and_oled)

except Exception as e:
    oled.show_message("FATAL ERROR", str(e))
