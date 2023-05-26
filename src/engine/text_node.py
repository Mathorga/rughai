from typing import Optional
import pyglet

from engine.settings import settings, Builtins
from engine.node import PositionNode

class TextNode(PositionNode):
    def __init__(
        self,
        x: float = 0,
        y: float = 0,
        width: int = 0,
        height: int = 0,
        color: tuple = (0x00, 0x00, 0x00, 0xFF),
        text: str = "_content_",
        scaling: int = 1,
        font_name: Optional[str] = settings[Builtins.FONT_NAME],
        font_size: int = 6,
        batch: Optional[pyglet.graphics.Batch] = None
    ) -> None:
        super().__init__(
            x = x,
            y = y
        )

        self.text = text

        self.__scaling = scaling

        self.label = pyglet.text.Label(
            text = text,
            x = x * scaling,
            y = y * scaling,
            font_name = font_name,
            font_size = font_size * scaling,
            anchor_x = "center",
            anchor_y = "center",
            color = color,
            batch = batch
        )

    def delete(self) -> None:
        self.label.delete()

    def set_position(
        self,
        x = None,
        y = None
    ) -> None:
        if x is not None:
            self.x = x
            self.label.x = x * self.__scaling

        if y is not None:
            self.y = y
            self.label.y = y * self.__scaling

    def set_opacity(self, opacity: float):
        self.label.opacity = opacity

    def set_text(self, text: str):
        self.label.text = text

    def draw(self) -> None:
        self.label.draw()