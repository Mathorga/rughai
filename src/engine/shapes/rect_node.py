from typing import Optional, Tuple
import pyglet

from engine.settings import GLOBALS, Builtins
from engine.shapes.shape_node import ShapeNode

class RectNode(ShapeNode):
    def __init__(
        self,
        x: float = 0,
        y: float = 0,
        width: int = 0,
        height: int = 0,
        anchor_x: float = 0,
        anchor_y: float = 0,
        color: Tuple[int, int, int, int] = (0x00, 0x00, 0x00, 0xFF),
        batch: Optional[pyglet.graphics.Batch] = None
    ) -> None:
        super().__init__(
            x = x,
            y = y,
            color = color
        )

        self.__shape = pyglet.shapes.Rectangle(
            x = x * GLOBALS[Builtins.SCALING],
            y = y * GLOBALS[Builtins.SCALING],
            width = width * GLOBALS[Builtins.SCALING],
            height = height * GLOBALS[Builtins.SCALING],
            color = color,
            batch = batch
        )
        self.__shape.anchor_position = (anchor_x * GLOBALS[Builtins.SCALING], anchor_y * GLOBALS[Builtins.SCALING])

    def delete(self) -> None:
        self.__shape.delete()

    def set_color(self, color: Tuple[int, int, int]):
        super().set_color(color)

        self.__shape.color = color

    def set_position(
        self,
        position: Tuple[int, int]
    ) -> None:
        super().set_position(position)

        self.__shape.x = position[0] * GLOBALS[Builtins.SCALING]
        self.__shape.y = position[1] * GLOBALS[Builtins.SCALING]

    def set_opacity(self, opacity: float):
        self.__shape.opacity = opacity

    def draw(self) -> None:
        self.__shape.draw()