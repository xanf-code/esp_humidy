from machine import Pin
import dht
import time

class DHTSensor:
    def __init__(self, pin=15):
        self.sensor = dht.DHT22(Pin(pin))

    def read(self):
        try:
            self.sensor.measure()
            temp_c = self.sensor.temperature()
            humidity = self.sensor.humidity()
            temp_f = temp_c * 9 / 5 + 32
            return temp_c, temp_f, humidity
        except:
            return None, None, None

