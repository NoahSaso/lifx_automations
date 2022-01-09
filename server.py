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


async def set_light(light, color):
    try:
        # dont do rapid so we can catch error
        light.set_power(True)
        light.set_color(color, 500, rapid=True)
        return True
    except:
        return False


async def set_devices_and_return_missing(devices, color):
    print(f"Trying to set {devices} to {color}...")

    lights = []
    for device in devices:
        [mac, ip] = device.split("-")
        lights.append(Light(mac, ip))

    results = await asyncio.gather(*[set_light(l, color) for l in lights])

    success = [d for d, r in zip(devices, results) if r]
    missing = [d for d, r in zip(devices, results) if not r]
    if len(success) > 0:
        print(f"Success: {success}")
    if len(missing) > 0:
        print(f"Missing: {missing}")
    print()

    return missing


# color parameter format is 4 numbers separated by decimal points
# [hue (0-65535), saturation (0-65535), brightness (0-65535), Kelvin (2500-9000)]
# warm_dim = (6007, 49151, 20971, 3500)


@app.route("/color/<color>")
async def set_color(color):
    color = tuple(int(c) for c in color.split("."))

    print()
    missing = await set_devices_and_return_missing(DEVICES, color)

    if len(missing) > 0:
        # try to set color to missing lights 10 times
        for _ in range(10):
            missing = await set_devices_and_return_missing(
                missing,
                color,
            )

            if len(missing) == 0:
                print(f"All devices set to {color}")
                break
            await asyncio.sleep(5)

    if len(missing) > 0:
        print(f"Could not set {missing} to {color}")
        print()

    return "Done"


if __name__ == "__main__":
    if PRODUCTION:
        print(f"Launching in production mode on {HOST}:{PORT}...")
        waitress.serve(app, host=HOST, port=PORT, url_prefix=URL_PREFIX)
    else:
        app.run()
