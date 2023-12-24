from typing import Optional, Tuple
import pyglet

from engine.settings import GLOBALS, Keys
from engine.shapes.shape_node import ShapeNode

class CircleNode(ShapeNode):
    def __init__(
        self,
        x: float = 0,
        y: float = 0,
        radius: int = 0,
        color: tuple = (0x00, 0x00, 0x00, 0xFF),
        batch: Optional[pyglet.graphics.Batch] = None
    ) -> None:
        super().__init__(
            x = x,
            y = y,
            color = color
        )

        self.__radius = radius

        self.__shape = pyglet.shapes.Circle(
            x = x * GLOBALS[Keys.SCALING],
            y = y * GLOBALS[Keys.SCALING],
            radius = radius * GLOBALS[Keys.SCALING],
            color = color,
            batch = batch
        )

    def delete(self) -> None:
        self.__shape.delete()

    def set_color(self, color: Tuple[int, int, int]):
        super().set_color(color)

        self.__shape.color = color

    def set_position(self, position: Tuple[int, int]) -> None:
        self.x = position[0]
        self.__shape.x = self.x * GLOBALS[Keys.SCALING]

        self.y = position[1]
        self.__shape.y = self.y * GLOBALS[Keys.SCALING]

    def set_opacity(self, opacity: float):
        self.__shape.opacity = opacity