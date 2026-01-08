import urequests
import time

class HeaterController:
    def __init__(self):
        self.turn_off_url = "https://maker.ifttt.com/trigger/turn_off/with/key/eWIgaqWsz6E7N0H1ShKiGwKTW2We9aekZ_kpcVt7Erw"
        self.turn_on_url = "https://maker.ifttt.com/trigger/turn_on_heater/with/key/eWIgaqWsz6E7N0H1ShKiGwKTW2We9aekZ_kpcVt7Erw"

        self.TEMP_HIGH = 27.0  # Turn off heater when >= 27°C
        self.TEMP_LOW = 21.0   # Turn on heater when <= 21°C

        self.heater_state = None  # None = unknown, True = on, False = off
        self.last_webhook_call = 0
        self.min_call_interval = 10  # Minimum seconds between webhook calls

    def check_and_control(self, temp_c):
        """
        Check temperature and control heater based on thresholds.
        Returns: (action_taken, message) tuple
        """
        if temp_c is None:
            return False, "No temperature reading"

        current_time = time.time()

        if current_time - self.last_webhook_call < self.min_call_interval:
            return False, "Rate limited"

        if temp_c >= self.TEMP_HIGH and self.heater_state != False:
            success = self._turn_off_heater(temp_c)
            if success:
                self.heater_state = False
                self.last_webhook_call = current_time
                return True, f"Heater OFF (temp: {temp_c}°C)"
            return False, "Failed to turn off heater"

        elif temp_c <= self.TEMP_LOW and self.heater_state != True:
            success = self._turn_on_heater(temp_c)
            if success:
                self.heater_state = True
                self.last_webhook_call = current_time
                return True, f"Heater ON (temp: {temp_c}°C)"
            return False, "Failed to turn on heater"

        # Temperature in deadband (21 < temp < 27), maintain current state
        return False, f"Temp OK ({temp_c}°C)"

    def _turn_off_heater(self, temp_c):
        try:
            print(f"[HEATER] Turning OFF - Temperature: {temp_c}°C >= {self.TEMP_HIGH}°C")
            r = urequests.get(self.turn_off_url, timeout=5)
            status = r.status_code
            r.close()

            if status == 200:
                print("[HEATER] Successfully turned OFF")
                return True
            else:
                print(f"[HEATER] Turn OFF failed - HTTP {status}")
                return False

        except Exception as e:
            print(f"[HEATER] Turn OFF error: {e}")
            return False

    def _turn_on_heater(self, temp_c):
        try:
            print(f"[HEATER] Turning ON - Temperature: {temp_c}°C <= {self.TEMP_LOW}°C")
            r = urequests.get(self.turn_on_url, timeout=5)
            status = r.status_code
            r.close()

            if status == 200:
                print("[HEATER] Successfully turned ON")
                return True
            else:
                print(f"[HEATER] Turn ON failed - HTTP {status}")
                return False

        except Exception as e:
            print(f"[HEATER] Turn ON error: {e}")
            return False

    def get_status(self):
        if self.heater_state is None:
            return "UNKNOWN"
        elif self.heater_state:
            return "ON"
        else:
            return "OFF"
