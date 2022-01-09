from dotenv import load_dotenv
import os
import re

load_dotenv()
DEVICES = os.getenv("DEVICES", "").split(",")
PRODUCTION = os.getenv("PRODUCTION", "false") == "true"
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", "5439"))
URL_PREFIX = os.getenv("URL_PREFIX", "")
WIFI = os.getenv("WIFI")


# color parameter format is 4 numbers separated by decimal points
# hue (0-65535), saturation (0-65535), brightness (0-65535), Kelvin (1500-9000)
# colors:
# warm_dim = (6007, 49151, 20971, 3500)
COLOR_REGEX = re.compile(r"^\d{1,5}\.\d{1,5}\.\d{1,5}\.\d{4}$")

NUMBER_REGEX = r"^\d+$"

ALLOWED_KEYS = ["color", "power"]
ALLOWED_POWERS = ["on", "off"]

MESSAGES = {
    "INVALID_COLOR": "Please provide 4 numbers separated by periods: hue (0-65535), saturation (0-65535), brightness (0-65535), Kelvin (1500-9000)",
    "INVALID_DEVICE_ID": f"Valid IDs are 0-{len(DEVICES) - 1}",
    "INVALID_KEY": f"Valid keys are {ALLOWED_KEYS}",
    "INVALID_POWER": f"Valid powers are {ALLOWED_POWERS}",
    "GENERIC_FAILURE": "Failed to communicate with the light(s). Check the log for more details.",
}
