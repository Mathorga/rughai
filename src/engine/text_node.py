from typing import Optional
import pyglet

from engine.node import PositionNode

class TextNode(PositionNode):
    def __init__(
        self,
        x: int = 0,
        y: int = 0,
        width: int = 0,
        height: int = 0,
        color: tuple = (0x00, 0x00, 0x00, 0xFF),
        text: str = "_content_",
        scaling: int = 1,
        font_name: Optional[str] = None,
        ui: bool = False,
        batch: Optional[pyglet.graphics.Batch] = None
    ) -> None:
        super().__init__(
            x = x,
            y = y
        )

        self.__width = width
        self.__height = height
        self.text = text

        self.__scaling = scaling

        self.__label = pyglet.text.Label(
            text = text,
            x = x * scaling,
            y = y * scaling,
            width = width * scaling,
            height = height * scaling,
            font_name = font_name,
            font_size = 32,
            anchor_x = "center",
            anchor_y = "center",
            color = color,
            batch = batch
        )

    def delete(self) -> None:
        self.__label.delete()

    def set_position(
        self,
        x = None,
        y = None
    ) -> None:
        if x is not None:
            self.x = x
            self.__label.x = x * self.__scaling

        if y is not None:
            self.y = y
            self.__label.y = y * self.__scaling

    def set_opacity(self, opacity: int):
        self.__label.opacity = opacity

    def draw(self) -> None:
        self.__label.draw()