from flask import Flask
from dotenv import load_dotenv
from lifxlan import LifxLAN, light
import os

app = Flask(__name__)
lifx = LifxLAN()

load_dotenv()
NAMES = os.getenv("NAMES", "").split(",")

# [hue (0-65535), saturation (0-65535), brightness (0-65535), Kelvin (2500-9000)]
COLORS = {
    "warm_dim": (6007, 49151, 20971, 3500),
}


def set_them_lights_and_return_missing(names, color):
    print(f"Trying to set {names} to {color}...")

    group = lifx.get_devices_by_name(NAMES)

    group.set_power(True)
    group.set_color(color)

    light_names = set([d.get_label() for d in group.get_device_list()])
    print(f"Set {light_names} to {color}")

    missing_light_names = [name for name in NAMES if name not in light_names]
    return missing_light_names


@app.route("/warm_dim")
async def warm_dim():
    missing_light_names = set_them_lights_and_return_missing(NAMES, COLORS["warm_dim"])

    # try to set color to missing lights 10 times
    for _ in range(10):
        if len(missing_light_names) > 0:
            missing_light_names = set_them_lights_and_return_missing(
                missing_light_names, COLORS["warm_dim"]
            )

            if len(missing_light_names) == 0:
                break

    return "Done"


if __name__ == "__main__":
    app.run()
