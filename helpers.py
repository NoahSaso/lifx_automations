import asyncio
from lifxlan import Light


async def set_light_color(light, color):
    try:
        light.set_power(True)
        light.set_color(color, 1000)
        return True
    except:
        return False


async def set_light_power(light, power):
    try:
        light.set_power(power)
        return True
    except:
        return False


def get_light_for_device_str(device):
    [mac, ip] = device.split("-")
    return Light(mac, ip)


async def set_devices_color_and_return_missing(devices, color):
    print(f"Trying to set {devices} to {color}...")

    lights = [get_light_for_device_str(d) for d in devices]
    results = await asyncio.gather(*[set_light_color(l, color) for l in lights])

    success = [d for d, r in zip(devices, results) if r]
    missing = [d for d, r in zip(devices, results) if not r]
    if len(success) > 0:
        print(f"Success: {success}")
    if len(missing) > 0:
        print(f"Missing: {missing}")
    print()

    return missing


async def set_devices_color_persistently(devices, color):
    """
    Set devices to color, and keep trying to set them to that color until successful or timeout (10 attempts separated by 5 second intervals).

    :param devices: list of device strings
    :type devices: list of strings
    :param color: color to set
    :type color: (int, int, int, int)
    :return: list of device strings that failed to set
    :rtype: list of strings
    """

    missing = await set_devices_color_and_return_missing(devices, color)

    if len(missing) > 0:
        # try to set color to missing lights 10 times
        for _ in range(10):
            missing = await set_devices_color_and_return_missing(
                missing,
                color,
            )

            if len(missing) == 0:
                print(f"All devices set to {color}")
                break

            # give light time to come online
            await asyncio.sleep(5)

    if len(missing) > 0:
        print(f"Could not set {missing} to {color}")
        print()

    return missing
