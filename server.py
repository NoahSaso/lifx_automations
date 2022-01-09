from flask import Flask, request, jsonify
from lifxlan import LifxLAN
import traceback
import waitress

from config import *
from middleware import *
from helpers import *

app = Flask(__name__)
lifx = LifxLAN()


def json_success(status_code=200, **data):
    return jsonify(success=True, **data), status_code


def json_error(error, status_code=400):
    return jsonify(success=False, error=error), status_code


@app.route("/<device_id_str>/<key>", methods=["GET"])
async def device_get(device_id_str, key):
    params, validation_error = validate_many(
        (valid_device_id, (device_id_str,)),
        (valid_key, (key,)),
    )
    if validation_error:
        return json_error(validation_error)
    [device_id, key] = params

    ensure_wifi_connected()

    device = DEVICES[device_id]
    light = get_light_for_device_str(device)
    try:
        value = None
        if key == "color":
            value = ".".join(map(str, light.get_color()))
        elif key == "power":
            value = "on" if light.get_power() else "off"
        else:
            # should never happen
            raise json_error(f"{key} not implemented")

        return json_success(**{key: value})
    except Exception as err:
        print(f"Failed to get {key} for {device}")
        print(err)
        traceback.print_exc()
        return json_error(str(err))


@app.route("/<device_id_str>/<key>", methods=["POST"])
async def device_post(device_id_str, key):
    params, validation_error = validate_many(
        (valid_device_id, (device_id_str,)),
        (valid_key, (key,)),
    )
    if validation_error:
        return json_error(validation_error)
    [device_id, key] = params

    ensure_wifi_connected()

    device = DEVICES[device_id]
    if key == "color":
        color, validation_error = valid_color(request.json.get("color"))
        if validation_error:
            return json_error(validation_error)

        try:
            await set_devices_color_persistently([device], color)
            return json_success()
        except Exception as err:
            print(f"Failed to set color = {color} for {device}")
            print(err)
            traceback.print_exc()
            return json_error(str(err))
    elif key == "power":
        power, validation_error = valid_power(request.json.get("power"))
        if validation_error:
            return json_error(validation_error)

        try:
            get_light_for_device_str(device).set_power(power)
            return json_success()
        except Exception as err:
            print(f"Failed to set power = {power} for {device}")
            print(err)
            traceback.print_exc()
            return json_error(str(err))

    # should never happen
    return json_error(f"{key} not implemented")


@app.route("/color", methods=["POST"])
async def all_color():
    color, validation_error = valid_color(request.json.get("color"))
    if validation_error:
        return json_error(validation_error)

    ensure_wifi_connected()

    missing = await set_devices_color_persistently(DEVICES, color)

    if len(missing) == len(DEVICES):
        return json_error("No lights online")
    # missing = list of device IDs that were not set
    return json_success(missing=list(map(DEVICES.index, missing)))


if __name__ == "__main__":
    if PRODUCTION:
        print(f"Launching in production mode on {HOST}:{PORT}...")
        waitress.serve(app, host=HOST, port=PORT, url_prefix=URL_PREFIX)
    else:
        app.run()
