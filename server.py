from flask import Flask
from dotenv import load_dotenv
from lifxlan import LifxLAN, Light
import os
import asyncio
import waitress

app = Flask(__name__)
lifx = LifxLAN()

load_dotenv()
DEVICES = os.getenv("DEVICES", "").split(",")
PRODUCTION = os.getenv("PRODUCTION", "false") == "true"
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", "5439"))
URL_PREFIX = os.getenv("URL_PREFIX", "")

# [hue (0-65535), saturation (0-65535), brightness (0-65535), Kelvin (2500-9000)]
COLORS = {
    "warm_dim": (6007, 49151, 20971, 3500),
}


def set_devices_and_return_missing(devices, color):
    print(f"Trying to set {devices} to {color}...")

    success = []
    missing = []
    for device in devices:
        [mac, ip] = device.split("-")
        l = Light(mac, ip)

        try:
            # dont do rapid so we can catch error
            l.set_power(True)
            l.set_color(color, rapid=True)
            success.append(device)
        except:
            missing.append(device)

    print(f"Set {success} to {color}")

    return missing


@app.route("/warm_dim")
async def warm_dim():
    missing = set_devices_and_return_missing(DEVICES, COLORS["warm_dim"])

    if len(missing) > 0:
        # try to set color to missing lights 10 times
        for _ in range(10):
            missing = set_devices_and_return_missing(
                missing,
                COLORS["warm_dim"],
            )

            if len(missing) == 0:
                break
            await asyncio.sleep(5)

    return "Done"


if __name__ == "__main__":
    if PRODUCTION:
        print(f"Launching in production mode on {HOST}:{PORT}...")
        waitress.serve(app, host=HOST, port=PORT, url_prefix=URL_PREFIX)
    else:
        app.run()
