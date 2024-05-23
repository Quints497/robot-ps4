import logging
import subprocess
import time

import evdev
from evdev import InputDevice


def ensure_device_connected(logger: logging.Logger, mac_address: str) -> None:
    """
    Ensures that the PS4 controller is connected via Bluetooth.

    Args:
        logger (logging.Logger): Logger instance for logging.
        mac_address (str): MAC address of the PS4 controller.
    """
    logger.info("Connecting to controller...")
    try:
        device_info = run_command(f"bluetoothctl info {mac_address}")
        if "Connected: no" in device_info:
            run_command(f"bluetoothctl connect {mac_address}")
            run_command(f"bluetoothctl trust {mac_address}")
    except Exception as e:
        logger.error(f"Error connecting to device: {e}")
        raise


def find_controller(logger: logging.Logger) -> InputDevice:
    """
    Finds the input device corresponding to the PS4 controller.

    Args:
        logger (logging.Logger): Logger instance for logging.

    Raises:
        SystemExit: If the PS4 controller cannot be found.

    Returns:
        InputDevice: The input device for the PS4 controller.
    """
    logger.info("Finding controller...")
    try:
        devices = [evdev.InputDevice(path) for path in evdev.list_devices()]
        for device in devices:
            logger.info(f"Device found: {device.path} - {device.name}")
            if "Wireless Controller" in device.name:
                logger.info("PS4 controller connected.")
                return InputDevice(device.path)
        logger.warning("PS4 controller not found. Retrying...")
        time.sleep(2)
        return find_controller(logger)
    except Exception as e:
        logger.error(f"Error finding PS4 controller: {e}")
        raise SystemExit(1)


def run_command(command: str) -> str:
    """
    Runs a shell command and captures its output.

    Args:
        command (str): The command to run.

    Returns:
        str: The standard output from the command.
    """
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"Error: {result.stderr}")
    return result.stdout
