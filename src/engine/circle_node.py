from typing import Optional, Tuple
import pyglet

from engine.node import PositionNode
from engine.settings import GLOBALS, Builtins

class CircleNode(PositionNode):
    def __init__(
        self,
        x: float = 0,
        y: float = 0,
        z: float = 0.0,
        radius: int = 0,
        color: tuple = (0x00, 0x00, 0x00, 0xFF),
        batch: Optional[pyglet.graphics.Batch] = None
    ) -> None:
        super().__init__(
            x = x,
            y = y,
            z = z
        )

        self.__radius = radius

        self.__shape = pyglet.shapes.Circle(
            x = x * GLOBALS[Builtins.SCALING],
            y = y * GLOBALS[Builtins.SCALING],
            radius = radius * GLOBALS[Builtins.SCALING],
            color = color,
            batch = batch
        )

    def delete(self) -> None:
        self.__shape.delete()

    def set_position(self, position: Tuple[int, int]) -> None:
        self.x = position[0]
        self.__shape.x = self.x * GLOBALS[Builtins.SCALING]

        self.y = position[1]
        self.__shape.y = self.y * GLOBALS[Builtins.SCALING]

    def set_opacity(self, opacity: float):
        self.__shape.opacity = opacity