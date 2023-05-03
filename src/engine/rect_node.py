from typing import Optional, Tuple
import pyglet

from engine.node import PositionNode

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
        scaling: int = 1,
        batch = None,
        group = None
    ) -> None:
        super().__init__(
            x = x,
            y = y
        )

        self.__width = width
        self.__height = height
        self.__anchor_x = anchor_x
        self.__anchor_y = anchor_y

        self.__scaling = scaling

        self.__shape = pyglet.shapes.Rectangle(
            x = x * scaling,
            y = y * scaling,
            width = width * scaling,
            height = height * scaling,
            color = color,
            batch = batch,
            group = group
        )
        self.__shape.anchor_position = (anchor_x * scaling, anchor_y * scaling)

    def delete(self) -> None:
        self.__shape.delete()

    def set_position(
        self,
        position: Tuple[int, int]
    ) -> None:
        self.x = position[0]
        self.__shape.x = position[0] * self.__scaling

        self.y = position[1]
        self.__shape.y = position[1] * self.__scaling

    def set_opacity(self, opacity: float):
        self.__shape.opacity = opacity

    def draw(self) -> None:
        self.__shape.draw()