from typing import Optional, Tuple
import pyglet

from engine.settings import GLOBALS, Keys
from engine.shapes.shape_node import ShapeNode


class LineNode(ShapeNode):
    def __init__(
        self,
        color: tuple[int, int, int, int] = (0xFF, 0xFF, 0xFF, 0xFF),
        x: float = 0.0,
        y: float = 0.0,
        delta_x: float = 0.0,
        delta_y: float = 0.0,
        batch: Optional[pyglet.graphics.Batch] = None
    ) -> None:
        super().__init__(x, y, color)

        self.delta_x = delta_x
        self.delta_y = delta_y

        self.__shape = pyglet.shapes.Line(
            x = x * GLOBALS[Keys.SCALING],
            y = y * GLOBALS[Keys.SCALING],
            x2 = (x + delta_x) * GLOBALS[Keys.SCALING],
            y2 = (y + delta_y) * GLOBALS[Keys.SCALING],
            color = color,
            width = 1 * GLOBALS[Keys.SCALING],
            batch = batch
        )

        # self.__shape = pyglet.shapes.Line(
        #     x = -1000 * GLOBALS[Builtins.SCALING],
        #     y = 80 * GLOBALS[Builtins.SCALING],
        #     x2 = 1000 * GLOBALS[Builtins.SCALING],
        #     y2 = 80 * GLOBALS[Builtins.SCALING],
        #     width = 1,
        #     batch = batch
        # )

    def delete(self) -> None:
        self.__shape.delete()

    def set_color(self, color: tuple[int, int, int]):
        super().set_color(color)

        self.__shape.color = color

    def set_position(
        self,
        position: tuple[float, float]
    ) -> None:
        super().set_position(position)

        self.__shape.x = position[0] * GLOBALS[Keys.SCALING]
        self.__shape.y = position[1] * GLOBALS[Keys.SCALING]

    def set_delta(
        self,
        delta: tuple[float, float]
    ) -> None:
        self.delta_x = delta[0]
        self.delta_y = delta[1]

        self.__shape.x2 = (self.x + delta[0]) * GLOBALS[Keys.SCALING]
        self.__shape.y2 = (self.y + delta[1]) * GLOBALS[Keys.SCALING]

    def set_opacity(self, opacity: float):
        self.__shape.opacity = opacity

    def draw(self) -> None:
        self.__shape.draw()
