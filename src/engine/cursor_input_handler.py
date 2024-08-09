import pyglet
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
        "__up_keys",
        "__left_keys",
        "__down_keys",
        "__right_keys"
    )

    def __init__(
        self,
        kick_time: float = 0.3,
        step_time: float = 0.1,
        up_keys: list[int] | None = None,
        left_keys: list[int] | None = None,
        down_keys: list[int] | None = None,
        right_keys: list[int] | None = None,
    ) -> None:
        self.__movement: pm.Vec2 = pm.Vec2()
        self.__kick_time: float = kick_time
        self.__elapsed_kick: float = 0.0
        self.__step_time: float = step_time
        self.__elapsed_step: float = 0.0

        self.__up_keys: list[int] = up_keys if up_keys is not None else []
        self.__left_keys: list[int] = left_keys if left_keys is not None else []
        self.__down_keys: list[int] = down_keys if down_keys is not None else []
        self.__right_keys: list[int] = right_keys if right_keys is not None else []

    def update(self, dt: float) -> None:
        super().update(dt)

        movement_started: bool = controllers.INPUT_CONTROLLER.get_cursor_movement_press(
            up_keys = self.__up_keys,
            left_keys = self.__left_keys,
            down_keys = self.__down_keys,
            right_keys = self.__right_keys
        )
        movement_ended: bool = controllers.INPUT_CONTROLLER.get_cursor_movement_release(
            up_keys = self.__up_keys,
            left_keys = self.__left_keys,
            down_keys = self.__down_keys,
            right_keys = self.__right_keys
        )
        move_input: pm.Vec2 = controllers.INPUT_CONTROLLER.get_cursor_movement_vec(
            up_keys = self.__up_keys,
            left_keys = self.__left_keys,
            down_keys = self.__down_keys,
            right_keys = self.__right_keys
        )

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