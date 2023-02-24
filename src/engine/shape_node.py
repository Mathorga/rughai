import pyglet

from engine.node import PositionNode

class ShapeNode(PositionNode):
    def __init__(
        self,
        x: int = 0,
        y: int = 0,
        width: int = 0,
        height: int = 0,
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
        self.__shape.anchor_position = (0, 0)

    def set_position(
        self,
        x = None,
        y = None
    ) -> None:
        if x is not None:
            self.x = x
            self.__shape.x = x * self.__scaling

        if y is not None:
            self.y = y
            self.__shape.y = y * self.__scaling

    def set_opacity(self, opacity: int):
        self.__shape.opacity = opacity

    def draw(self) -> None:
        self.__shape.draw()