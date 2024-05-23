import logging
import os
from dotenv import load_dotenv

# Load environment variables from a .env file if it exists
load_dotenv()

PATH_TO_LOGS = os.getenv("PATH_TO_LOGS")

# Ensure the logs directory exists
if not os.path.exists(PATH_TO_LOGS):
    os.makedirs(PATH_TO_LOGS, exist_ok=True)


def setup_logging(
    log_file: str,
    level: int = logging.INFO,
    format: str = "%(asctime)s - %(levelname)s - %(message)s",
) -> logging.Logger:
    """
    Sets up logging configuration and returns a logger instance.

    Args:
        log_file (str): The file path of the log file.
        level (int): The logging level.
        format (str): The logging format.

    Returns:
        logging.Logger: Configured logger instance.
    """
    logging.basicConfig(
        filename=f"logs/{log_file}",
        level=level,
        format=format,
    )
    return logging.getLogger(__name__)


# Robot motor speeds
LEFT_MOTOR_SPEED = float(os.getenv("LEFT_MOTOR_SPEED", 0.5))
RIGHT_MOTOR_SPEED = float(os.getenv("RIGHT_MOTOR_SPEED", 0.51))

# Variable speeds
SLOW_SPEED = float(os.getenv("SLOW_SPEED", 0.25))
NORMAL_SPEED = float(os.getenv("NORMAL_SPEED", 0.5))
FAST_SPEED = float(os.getenv("FAST_SPEED", 0.75))
SUPER_SPEED = float(os.getenv("SUPER_SPEED", 0.99))

# Joystick deadzones
HIGH_DEADZONE = int(os.getenv("HIGH_DEADZONE", 150))
LOW_DEADZONE = int(os.getenv("LOW_DEADZONE", 100))

# PS4 controller MAC address
MAC_ADDRESS = os.getenv("MAC_ADDRESS")
if not MAC_ADDRESS:
    raise ValueError("MAC_ADDRESS environment variable not set")
