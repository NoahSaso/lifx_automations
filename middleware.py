import subprocess
import re

from config import *


def validate_many(*validators):
    """
    Runs multiple validators and returns the first error.

    :param validators: list of validator functions with arguments to run
    :type validators: list of (function, tuple of any)

    :returns: (validated_values, None) if all are valid or (None, validation_error) otherwise
    :rtype: (list of any, None) | (None, string)
    """

    validated_values = []
    for validate_fn, args in validators:
        value, validation_error = validate_fn(*args)
        if validation_error:
            return None, validation_error

        validated_values.append(value)

    return validated_values, None


def valid_device_id(device_id_str):
    if not device_id_str or not re.match(NUMBER_REGEX, device_id_str):
        return None, MESSAGES["INVALID_DEVICE_ID"]

    device_id = int(device_id_str)
    if device_id < 0 or device_id >= len(DEVICES):
        return None, MESSAGES["INVALID_DEVICE_ID"]

    return device_id, None


def valid_key(key):
    if not key or key not in ALLOWED_KEYS:
        return None, MESSAGES["INVALID_KEY"]

    return key, None

def valid_color(color_str):
    if not color_str or not COLOR_REGEX.match(color_str):
        return None, MESSAGES["INVALID_COLOR"]

    color = tuple(map(int, color_str.split(".")))
    if (
        color[0] > 65535
        or color[1] > 65535
        or color[2] > 65535
        or color[3] < 1500
        or color[3] > 9000
    ):
        return None, MESSAGES["INVALID_COLOR"]

    return color, None


def valid_power(power):
    if not power or power not in ALLOWED_POWERS:
        return None, MESSAGES["INVALID_POWER"]

    return power, None


def ensure_wifi_connected():
    # if provided wi-fi, try to connect
    if WIFI and WIFI not in subprocess.check_output(
        "netsh wlan show interfaces"
    ).decode("utf-8"):
        print(f"Not connected to {WIFI}. Connecting...")
        subprocess.run(f'netsh wlan connect name="{WIFI}" ssid="{WIFI}"')
