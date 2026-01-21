import urequests
import machine
import json

class OTAUpdater:
    def __init__(self):
        self.manifest_url = "https://raw.githubusercontent.com/xanf-code/esp_humidy/main/manifest.json"
        self.current_version = self._read_local_version()

    def _read_local_version(self):
        try:
            with open("manifest.json", "r") as f:
                manifest = json.load(f)
                return manifest.get("version", "0.0.0")
        except:
            return "0.0.0"

    def check_for_update(self):
        try:
            r = urequests.get(self.manifest_url)
            manifest = r.json()
            r.close()

            latest_version = manifest.get("version")
            files = manifest.get("files")
            base_url = manifest.get("base_url")

            if not latest_version or not files or not base_url:
                return False, None, None

            if latest_version != self.current_version:
                return True, latest_version, (files, base_url)

            return False, latest_version, None

        except Exception as e:
            print("OTA check failed:", e)
            return False, None, None

    def install_update(self, files, base_url):
        print("Starting OTA update...")

        for filename in files:
            url = base_url + filename
            print("Downloading:", url)

            try:
                r = urequests.get(url)
                code = r.text
                r.close()
            except Exception as e:
                print("Failed to download", filename, ":", e)
                return  # abort update safely

            try:
                with open(filename, "w") as f:
                    f.write(code)
                print("Updated:", filename)
            except Exception as e:
                print("Failed to write", filename, ":", e)
                return  # abort update safely

        print("OTA update complete, rebooting...")
        machine.reset()

