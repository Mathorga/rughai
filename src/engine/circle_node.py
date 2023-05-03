from typing import Optional, Tuple
import pyglet

from engine.node import PositionNode

class CircleNode(PositionNode):
    def __init__(
        self,
        x: float = 0,
        y: float = 0,
        z: float = 0.0,
        radius: int = 0,
        color: tuple = (0x00, 0x00, 0x00, 0xFF),
        scaling: int = 1,
        batch: Optional[pyglet.graphics.Batch] = None
    ) -> None:
        super().__init__(
            x = x,
            y = y,
            z = z
        )

        self.__radius = radius

        self.__scaling = scaling

        self.__shape = pyglet.shapes.Circle(
            x = x * scaling,
            y = y * scaling,
            radius = radius * scaling,
            color = color,
            batch = batch
        )

    def delete(self) -> None:
        self.__shape.delete()

    def set_position(self, position: Tuple[int, int]) -> None:
        self.x = position[0]
        self.__shape.x = self.x * self.__scaling

        self.y = position[1]
        self.__shape.y = self.y * self.__scaling

    def set_opacity(self, opacity: float):
        self.__shape.opacity = opacity