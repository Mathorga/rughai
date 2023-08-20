import pyglet.math as pm
from pyglet.window import key

from engine import controllers

class CursorInput:

    def get_interaction(self) -> bool:
        """
        Returns whether the interact button was pressed or not, either on controller or keyboard.
        """

        return controllers.INPUT_CONTROLLER.key_presses.get(key.L, False) or controllers.INPUT_CONTROLLER.button_presses.get("a", False)

    def get_move_input(self) -> pm.Vec2:
        """
        Returns the movement vector from keyboard and controller.
        """

        w = controllers.INPUT_CONTROLLER.key_presses.get(key.W, False)
        a = controllers.INPUT_CONTROLLER.key_presses.get(key.A, False)
        s = controllers.INPUT_CONTROLLER.key_presses.get(key.S, False)
        d = controllers.INPUT_CONTROLLER.key_presses.get(key.D, False)

        return pm.Vec2(
            1 if d else 0 - 1 if a else 0,
            1 if w else 0 - 1 if s else 0
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