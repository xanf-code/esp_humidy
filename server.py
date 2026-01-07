import socket
import json
import time

class HTTPServer:
    def __init__(self):
        self.last_temp_c = None
        self.last_temp_f = None
        self.last_humidity = None

    def update_readings(self, temp_c, temp_f, humidity):
        self.last_temp_c = temp_c
        self.last_temp_f = temp_f
        self.last_humidity = humidity

    def start(self, update_callback):
        s = socket.socket()
        s.bind(("0.0.0.0", 80))
        s.listen(1)
        s.settimeout(0.1)

        while True:
            # Periodic sensor/UI update (same logic as before)
            update_callback()

            try:
                conn, addr = s.accept()
                req = conn.recv(1024).decode()

                if "GET /reading" in req:
                    body = json.dumps({
                        "temperature_c": self.last_temp_c,
                        "temperature_f": self.last_temp_f,
                        "humidity": self.last_humidity,
                        "unit": "C"
                    })
                    conn.send(
                        "HTTP/1.1 200 OK\r\n"
                        "Content-Type: application/json\r\n\r\n"
                    )
                    conn.send(body)
                else:
                    conn.send("HTTP/1.1 404 Not Found\r\n\r\n")

                conn.close()
            except OSError:
                pass

            time.sleep(0.05)  # same CPU yield

