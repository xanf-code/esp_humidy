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
                version = manifest.get("version", "0.0.0")
                print("Local version:", version)
                return version
        except Exception as e:
            print("Failed to read local version:", e)
            return "0.0.0"

    def _compare_versions(self, v1, v2):
        """Compare semantic versions. Returns True if v2 > v1"""
        try:
            v1_parts = [int(x) for x in v1.split('.')]
            v2_parts = [int(x) for x in v2.split('.')]

            for i in range(max(len(v1_parts), len(v2_parts))):
                p1 = v1_parts[i] if i < len(v1_parts) else 0
                p2 = v2_parts[i] if i < len(v2_parts) else 0
                if p2 > p1:
                    return True
                elif p2 < p1:
                    return False
            return False
        except:
            return v2 != v1

    def check_for_update(self):
        try:
            r = urequests.get(self.manifest_url)
            manifest = r.json()
            r.close()

            latest_version = manifest.get("version")
            files = manifest.get("files")
            base_url = manifest.get("base_url")

            print("Remote version:", latest_version)
            print("Current version:", self.current_version)

            if not latest_version or not files or not base_url:
                return False, None, None

            # Only update if remote version is NEWER
            if self._compare_versions(self.current_version, latest_version):
                print("Update available!")
                return True, latest_version, (files, base_url)

            print("Already up to date")
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

