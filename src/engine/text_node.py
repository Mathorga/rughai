from typing import Optional, Tuple
import pyglet

from engine.settings import settings, Builtins
from engine.node import PositionNode

class TextNode(PositionNode):
    def __init__(
        self,
        x: float = 0,
        y: float = 0,
        text: str = "_content_",
        align: str = "center",
        anchor_x: str = "center",
        anchor_y: str = "center",
        width: float = settings[Builtins.VIEW_WIDTH],
        height: Optional[float] = None,
        color: tuple = (0x00, 0x00, 0x00, 0xFF),
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
            multiline = True,
            width = width * scaling,
            height = height * scaling if height is not None else None,
            font_name = font_name,
            font_size = font_size * scaling,
            align = align,
            anchor_x = anchor_x,
            anchor_y = anchor_y,
            color = color,
            batch = batch
        )

    def delete(self) -> None:
        self.label.delete()

    def set_position(
        self,
        position: Tuple[float, float],
        z: Optional[float] = None
    ):
        self.x = position[0]
        self.label.x = position[0] * self.__scaling

        self.y = position[1]
        self.label.y = position[1] * self.__scaling

    def set_opacity(self, opacity: float):
        self.label.opacity = opacity

    def set_text(self, text: str):
        self.label.text = text

    def draw(self) -> None:
        self.label.draw()