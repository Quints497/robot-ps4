import time
from typing import Dict, Optional

import evdev
from evdev import categorize, ecodes
from gpiozero import CamJamKitRobot

from robot_utils import ensure_device_connected, find_controller
from robot_ps4.config import (
    setup_logging,
    LEFT_MOTOR_SPEED,
    RIGHT_MOTOR_SPEED,
    SLOW_SPEED,
    NORMAL_SPEED,
    FAST_SPEED,
    SUPER_SPEED,
    HIGH_DEADZONE,
    LOW_DEADZONE,
    MAC_ADDRESS,
)


class PS4Controller:
    """
    This class represents a PS4 Controller that is used to control a robot. The robot is set up in such a way that the values for forward, backward, left, and right movements are reversed.

    Attributes:
    - robot: An instance of the CamJamKitRobot class that represents the robot being controlled.
    - key_map: A dictionary that maps the names of the buttons on the PS4 controller to their corresponding event codes.
    - leftmotorspeed, rightmotorspeed: The speeds of the left and right motors of the robot.
    - slow_speed, normal_speed, fast_speed, super_speed: The variable speeds that the robot can move at.
    - variable_speed_map: A dictionary that maps the names of the variable speeds to their current states (0 or 1).
    - HIGH_DEADZONE, LOW_DEADZONE: The high and low deadzones for the controller's joystick.
    - BUTTON_PRESS, BUTTON_RELEASE: Constants representing the states of a button press and release.
    - MAC_ADDRESS: The MAC address of the controller.
    - current_direction: The current direction that the robot is moving in.
    - direction_start_time: The time when the robot started moving in the current direction.
    - logger: A logger for logging information and errors.
    - controller: The controller device.

    Methods:
    - create_key_map: Creates a dictionary mapping the names of the buttons on the PS4 controller to their corresponding event codes.
    - get_variable_speeds: Retrieves the variable speeds for the robot's movement from environment variables.
    - get_motor_speeds: Retrieves the speeds of the left and right motors from environment variables.
    - get_deadzones: Retrieves the high and low deadzones for the controller's joystick from environment variables.
    - get_mac_address: Retrieves the MAC address of the controller from an environment variable.
    - connect_to_controller: Ensures the device is connected and finds the controller.
    - move: Moves the robot in a specified direction. Logs the duration of the movement if the direction changes.
    - spin: Makes the robot spin in a specified direction for one second.
    - modify_speed: Changes the speed of the robot based on the button pressed on the controller.
    - modify_speed_helper: Helper method for modify_speed. Changes the speed of the robot and updates the variable_speed_map.
    - handle_key_event: Handles key press and release events from the controller. Controls the movement and speed of the robot based on the button pressed or released.
    - handle_abs_event: Handles absolute movement events from the controller's joystick.
    - main: The main loop that reads events from the controller and handles them. Stops the robot and logs any errors that occur.
    """

    def __init__(self):
        """
        Initialises the PS4Controller by loading environment variables, setting up the robot, and connecting to the controller.
        """
        self.robot = CamJamKitRobot()
        self.logger = setup_logging("ps4_controller.log")
        self.key_map: Dict[str, int] = self.create_key_map()
        self.leftmotorspeed: float = LEFT_MOTOR_SPEED
        self.rightmotorspeed: float = RIGHT_MOTOR_SPEED
        self.SLOW: float = SLOW_SPEED
        self.NORMAL: float = NORMAL_SPEED
        self.FAST: float = FAST_SPEED
        self.SUPER: float = SUPER_SPEED
        self.variable_speed_map = {
            "slow": 0,
            "fast": 0,
            "super": 0,
        }
        self.HIGH_DEADZONE: int = HIGH_DEADZONE
        self.LOW_DEADZONE: int = LOW_DEADZONE
        self.BUTTON_PRESS = 1
        self.BUTTON_RELEASE = 0
        self.MAC_ADDRESS: str = MAC_ADDRESS
        self.current_direction: Optional[str] = None
        self.direction_start_time: Optional[float] = None
        self.controller = self.connect_to_controller()

    def create_key_map(self) -> Dict[str, int]:
        """
        Creates a dictionary mapping the names of the buttons on the PS4 controller to their corresponding event codes.

        Returns:
            Dict[str, int]: A dictionary with button names as keys and their event codes as values.
        """
        self.logger.info("Creating key map...")
        return {
            "x": 304,
            "square": 308,
            "triangle": 307,
            "circle": 305,
            "lt": 312,
            "lb": 310,
            "rt": 313,
            "rb": 311,
        }

    def connect_to_controller(self) -> evdev.InputDevice:
        """
        Ensures the device is connected and finds the controller.

        Returns:
            evdev.InputDevice: The input device representing the PS4 controller.
        """
        ensure_device_connected(self.logger, self.MAC_ADDRESS)

        return find_controller(self.logger)

    def move(self, direction: str) -> None:
        """
        Moves the robot in a specified direction. Logs the duration of the movement if the direction changes.

        Args:
            direction (str): The direction to move the robot.
        """
        if self.current_direction != direction:
            if self.current_direction is not None:
                duration = time.time() - self.direction_start_time
                self.logger.info(
                    f"Moving {self.current_direction} for {duration:.2f} seconds"
                )
            self.current_direction = direction
            self.direction_start_time = time.time()

        self.logger.debug(f"Moving {direction}")
        directions = {
            "forward": (-self.leftmotorspeed, -self.rightmotorspeed),
            "backward": (self.leftmotorspeed, self.rightmotorspeed),
            "left": (-self.leftmotorspeed, self.rightmotorspeed),
            "right": (self.leftmotorspeed, -self.rightmotorspeed),
            "sharp_left": (1, -1),
            "sharp_right": (-1, 1),
            "stop": (0, 0),
        }
        self.robot.value = directions.get(direction, (0, 0))

    def spin(self, direction: str) -> None:
        """
        Makes the robot spin in a specified direction for one second.

        Args:
            direction (str): The direction to spin the robot.
        """
        self.logger.info(f"Spinning {direction}")
        self.move(f"sharp_{direction}")
        time.sleep(1)
        self.move("stop")

    def modify_speed(self, event_code: int) -> None:
        """
        Changes the speed of the robot based on the button pressed on the controller.

        Args:
            event_code (int): The event code of the button pressed.
        """
        # slow speed
        if event_code == self.key_map["square"]:
            self.modify_speed_helper("slow")
        # fast speed
        elif event_code == self.key_map["x"]:
            self.modify_speed_helper("fast")
        # super speed
        elif event_code == self.key_map["circle"]:
            self.modify_speed_helper("super")

        self.logger.info(
            f"Left motor speed: {self.leftmotorspeed}, Right motor speed: {self.rightmotorspeed}"
        )

    def modify_speed_helper(self, speed_type: str) -> None:
        """
        Helper method for modify_speed. Changes the speed of the robot and updates the variable_speed_map.

        Args:
            speed_type (str): The type of speed to modify (slow, fast, super).
        """
        if self.variable_speed_map[speed_type] == 0:
            if speed_type == "slow":
                self.leftmotorspeed = self.SLOW
                self.rightmotorspeed = self.SLOW + 0.01
            elif speed_type == "fast":
                self.leftmotorspeed = self.FAST
                self.rightmotorspeed = self.FAST + 0.01
            elif speed_type == "super":
                self.leftmotorspeed = self.SUPER
                self.rightmotorspeed = self.SUPER + 0.01
            self.variable_speed_map[speed_type] = 1
        else:
            self.leftmotorspeed = self.NORMAL
            self.rightmotorspeed = self.NORMAL + 0.01
            self.variable_speed_map[speed_type] = 0

    def handle_key_event(self, event: evdev.InputEvent, button_is_held: bool) -> bool:
        """
        Handles key press and release events from the controller. Controls the movement and speed of the robot based on the button pressed or released.

        Args:
            event (evdev.InputEvent): The event from the controller.
            button_is_held (bool): Indicates if a button is currently being held down.

        Returns:
            bool: Updated state of button_is_held.
        """
        if event.value == self.BUTTON_PRESS:
            button_is_held = True
            # right bumper -> move forward
            if event.code == self.key_map["rb"]:
                self.move("forward")
            # left bumper -> move backward
            elif event.code == self.key_map["lb"]:
                self.move("backward")
        elif event.value == self.BUTTON_RELEASE:
            button_is_held = False
            # left bumper, right bumper -> releasing either stops the car
            if event.code in [
                self.key_map["lb"],
                self.key_map["rb"],
            ]:
                self.move("stop")
            # left trigger, right trigger -> spinning
            elif event.code in [
                self.key_map["lt"],
                self.key_map["rt"],
            ]:
                self.spin("right" if event.code == 313 else "left")
            # square button, x button, circle button -> modify speed
            elif event.code in [
                self.key_map["square"],
                self.key_map["x"],
                self.key_map["circle"],
            ]:
                self.modify_speed(event.code)
            # Exit the script if the triangle button is pressed
            elif event.code == self.key_map["triangle"]:
                raise KeyboardInterrupt

        return button_is_held

    def handle_abs_event(
        self, absevent: evdev.events.AbsEvent, button_is_held: bool
    ) -> None:
        """
        Handles absolute movement (x) events from the controller's joystick.

        Args:
            absevent (evdev.events.AbsEvent): The absolute movement event from the controller.
            button_is_held (bool): Indicates if a button is currently being held down.
        """
        if absevent.event.code == ecodes.ABS_X:
            if absevent.event.value >= self.HIGH_DEADZONE:
                self.move("right")
            elif absevent.event.value <= self.LOW_DEADZONE:
                self.move("left")
            else:
                if not button_is_held:
                    self.move("stop")

    def main(self) -> None:
        """
        The main loop that reads events from the controller and handles them. Stops the robot and logs any errors that occur.
        """
        try:
            button_is_held = False
            for event in self.controller.read_loop():
                if event.type == ecodes.EV_KEY:
                    button_is_held = self.handle_key_event(event, button_is_held)
                elif event.type == ecodes.EV_ABS:
                    absevent = categorize(event)
                    self.handle_abs_event(absevent, button_is_held)
        except KeyboardInterrupt:
            self.move("stop")
            self.logger.info("Controller script terminated.")
        except Exception as e:
            self.move("stop")
            self.logger.error(f"Error in main loop: {e}")


if __name__ == "__main__":
    ps4 = PS4Controller()
    ps4.main()
