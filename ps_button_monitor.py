import subprocess
import time

from evdev import ecodes

from robot_ps4.config import setup_logging
from robot_utils import find_controller

# Path to the PS4 controller script
PS4_CONTROLLER_SCRIPT = "robot_controller.py"  # Update this path as necessary

# The PS button code
PS_BUTTON_CODE = 316  # Code for the PS button


def run_ps4_controller_script():
    """
    Runs the PS4 controller script using subprocess.
    """
    subprocess.Popen(["python3", PS4_CONTROLLER_SCRIPT])


def main():
    """
    Main function to monitor for the PS button press and start the PS4 controller script.
    """
    logger = setup_logging("ps_button_monitor.log")
    while True:
        controller = find_controller(logger)
        if controller:
            logger.info("PS4 controller connected. Monitoring for PS button press...")
            for event in controller.read_loop():
                if (
                    event.type == ecodes.EV_KEY
                    and event.value == 1
                    and event.code == PS_BUTTON_CODE
                ):
                    logger.info("PS button pressed. Starting PS4 controller script...")
                    run_ps4_controller_script()
                    break
        else:
            logger.warning("PS4 controller not found. Retrying in 5 seconds...")
            time.sleep(5)


if __name__ == "__main__":
    main()
