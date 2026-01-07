from machine import I2C, Pin
import ssd1306

class OLEDDisplay:
    def __init__(self):
        i2c = I2C(0, scl=Pin(22), sda=Pin(21))
        self.oled = ssd1306.SSD1306_I2C(128, 64, i2c)

    def show_reading(self, time_str, temp_c, humidity):
        self.oled.fill(0)

        time_x = (128 - len(time_str) * 8) // 2
        self.oled.text(time_str, time_x, 0)
        self.oled.text("----------------", 0, 12)

        self.oled.text("Temp:", 0, 28)
        self.oled.text("{:.1f} C".format(temp_c), 60, 28)

        self.oled.text("Humidity:", 0, 48)
        self.oled.text("{:.1f} %".format(humidity), 80, 48)

        self.oled.show()

    def show_message(self, line1, line2=""):
        self.oled.fill(0)
        self.oled.text(line1, 0, 0)
        if line2:
            self.oled.text(line2, 0, 20)
        self.oled.show()

