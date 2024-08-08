import pyglet.math as pm

from engine import controllers
from engine.node import Node

class CursorInputHandler(Node):
    __slots__ = (
        "__movement",
        "__kick_time",
        "__elapsed_kick",
        "__step_time",
        "__elapsed_step",
    )

    def __init__(
        self,
        kick_time: float = 0.3,
        step_time: float = 0.1,
    ) -> None:
        self.__movement: pm.Vec2 = pm.Vec2()
        self.__kick_time: float = kick_time
        self.__elapsed_kick: float = 0.0
        self.__step_time: float = step_time
        self.__elapsed_step: float = 0.0

    def update(self, dt: float) -> None:
        super().update(dt)

        movement_started: bool = controllers.INPUT_CONTROLLER.get_cursor_movement_press()
        movement_ended: bool = controllers.INPUT_CONTROLLER.get_cursor_movement_release()
        move_input: pm.Vec2 = controllers.INPUT_CONTROLLER.get_cursor_movement_hold_vec()

        # Input was released, so stop counting for kick.
        if movement_ended:
            self.__elapsed_kick = 0.0

        if move_input.mag > 0.0:
            self.__elapsed_kick += dt
            self.__elapsed_step += dt

        if (self.__elapsed_kick > self.__kick_time and self.__elapsed_step > self.__step_time) or movement_started:
            self.__elapsed_step = 0.0
            self.__movement = move_input
        else:
            self.__movement = pm.Vec2()

    def get_movement(self) -> pm.Vec2:
        return self.__movement