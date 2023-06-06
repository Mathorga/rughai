from typing import Tuple
import pyglet

from engine.node import PositionNode
from engine.settings import GLOBALS, Builtins

class RectNode(PositionNode):
    def __init__(
        self,
        x: float = 0,
        y: float = 0,
        width: int = 0,
        height: int = 0,
        anchor_x: float = 0,
        anchor_y: float = 0,
        color: tuple = (0x00, 0x00, 0x00),
        batch = None,
        group = None
    ) -> None:
        super().__init__(
            x = x,
            y = y
        )

        self.__shape = pyglet.shapes.Rectangle(
            x = x * GLOBALS[Builtins.SCALING],
            y = y * GLOBALS[Builtins.SCALING],
            width = width * GLOBALS[Builtins.SCALING],
            height = height * GLOBALS[Builtins.SCALING],
            color = color,
            batch = batch,
            group = group
        )
        self.__shape.anchor_position = (anchor_x * GLOBALS[Builtins.SCALING], anchor_y * GLOBALS[Builtins.SCALING])

    def delete(self) -> None:
        self.__shape.delete()

    def set_position(
        self,
        position: Tuple[int, int]
    ) -> None:
        self.x = position[0]
        self.__shape.x = position[0] * GLOBALS[Builtins.SCALING]

        self.y = position[1]
        self.__shape.y = position[1] * GLOBALS[Builtins.SCALING]

    def set_opacity(self, opacity: float):
        self.__shape.opacity = opacity

    def draw(self) -> None:
        self.__shape.draw()