from typing import Optional, Tuple
import pyglet

from engine.settings import GLOBALS, Keys
from engine.shapes.shape_node import ShapeNode

class RectNode(ShapeNode):
    def __init__(
        self,
        x: float = 0.0,
        y: float = 0.0,
        z: float = 0.0,
        width: int = 0,
        height: int = 0,
        anchor_x: float = 0,
        anchor_y: float = 0,
        color: Tuple[int, int, int] = (0x00, 0x00, 0x00),
        batch: Optional[pyglet.graphics.Batch] = None
    ) -> None:
        super().__init__(
            x = x,
            y = y,
            z = z,
            color = color
        )

        self.__shape: pyglet.shapes.Rectangle = pyglet.shapes.Rectangle(
            x = x * GLOBALS[Keys.SCALING],
            y = y * GLOBALS[Keys.SCALING],
            width = width * GLOBALS[Keys.SCALING],
            height = height * GLOBALS[Keys.SCALING],
            color = color,
            group = pyglet.graphics.Group(order = int(z)),
            batch = batch
        )
        self.__shape.anchor_position = (anchor_x * GLOBALS[Keys.SCALING], anchor_y * GLOBALS[Keys.SCALING])

    def delete(self) -> None:
        self.__shape.delete()

    def set_color(self, color: Tuple[int, int, int]):
        super().set_color(color)

        self.__shape.color = color

    def set_position(
        self,
        position: Tuple[float, float],
        z: Optional[float] = None
    ) -> None:
        super().set_position(position)

        self.__shape.x = position[0] * GLOBALS[Keys.SCALING]
        self.__shape.y = position[1] * GLOBALS[Keys.SCALING]

        if z is not None:
            self.z = z

    def get_bounds(self) -> Tuple[float, float, float, float]:
        """
        Computes and returns the rectangle position and size in the form of a tuple defined as (x, y, width, height).
        """
        
        return (*self.get_position(), self.__shape.width, self.__shape.height)

    def set_bounds(self, bounds: Tuple[float, float, float, float]) -> None:
        """
        Sets the rectangle position and size.

        [bounds] is a tuple defined as (x, y, width, height).
        """

        self.set_position(bounds[:2])
        self.__shape.width = bounds[2] * GLOBALS[Keys.SCALING]
        self.__shape.height = bounds[3] * GLOBALS[Keys.SCALING]

    def set_opacity(self, opacity: float):
        self.__shape.opacity = opacity

    def draw(self) -> None:
        self.__shape.draw()