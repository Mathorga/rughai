import pyglet.math as pm
from pyglet.window import key

from engine import controllers

class PlayerInput:
    def get_modifier(self) -> bool:
        """
        Returns whether or not the modifier key is being pressed, either on controller or keyboard.
        """

        return controllers.INPUT_CONTROLLER[key.LSHIFT] or controllers.INPUT_CONTROLLER.buttons.get("leftshoulder", False)

    def get_sprint(self) -> bool:
        """
        Returns whether the sprint button was pressed or not, either on controller or keyboard.
        """

        return controllers.INPUT_CONTROLLER.key_presses.get(key.SPACE, False) or controllers.INPUT_CONTROLLER.button_presses.get("b", False)

    def get_interaction(self) -> bool:
        """
        Returns whether the interact button was pressed or not, either on controller or keyboard.
        """

        return controllers.INPUT_CONTROLLER.key_presses.get(key.L, False) or controllers.INPUT_CONTROLLER.button_presses.get("a", False)

    def get_main_atk(self) -> bool:
        """
        Returns whether the main attack button was pressed or not, either on controller or keyboard.
        """

        return controllers.INPUT_CONTROLLER.key_presses.get(key.M, False) or controllers.INPUT_CONTROLLER.button_presses.get("x", False)

    def get_secondary_atk(self) -> bool:
        """
        Returns whether the secondary attack button was pressed or not, either on controller or keyboard.
        """

        return controllers.INPUT_CONTROLLER.key_presses.get(key.K, False) or controllers.INPUT_CONTROLLER.button_presses.get("y", False)

    def get_fire_aim(self) -> bool:
        """
        Returns whether the range attack aim button was pressed or not.
        """

        return controllers.INPUT_CONTROLLER.triggers.get("lefttrigger", 0.0) > 0.0

    def get_fire_load(self) -> bool:
        """
        Returns whether the range attack load button was pressed or not.
        """

        return controllers.INPUT_CONTROLLER.triggers.get("righttrigger", 0.0) > 0.0

    def get_move_input(self) -> pm.Vec2:
        """
        Returns the movement vector from keyboard and controller.
        """

        stick = controllers.INPUT_CONTROLLER.sticks.get("leftstick", (0.0, 0.0))
        return pm.Vec2(
            (controllers.INPUT_CONTROLLER[key.D] - controllers.INPUT_CONTROLLER[key.A]) + stick[0],
            (controllers.INPUT_CONTROLLER[key.W] - controllers.INPUT_CONTROLLER[key.S]) + stick[1]
        )

    def get_look_input(self) -> pm.Vec2:
        """
        Returns the camera movement vector from keyboard and controller.
        """

        stick = controllers.INPUT_CONTROLLER.sticks.get("rightstick", (0.0, 0.0))
        return pm.Vec2(
            (controllers.INPUT_CONTROLLER[key.RIGHT] - controllers.INPUT_CONTROLLER[key.LEFT]) + stick[0],
            (controllers.INPUT_CONTROLLER[key.UP] - controllers.INPUT_CONTROLLER[key.DOWN]) + stick[1]
        )