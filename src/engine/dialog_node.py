from typing import Optional
import pyglet

from engine.node import PositionNode
from engine.settings import settings, Builtins
from engine.text_node import TextNode


class DialogNode(PositionNode):
    def __init__(
        self,
        x: float = 0.0,
        y: float = 0.0,
        scaling: int = 1,
        batch: Optional[pyglet.graphics.Batch] = None,
    ) -> None:
        super().__init__(x, y)

        self.on_text = "Goodbye, cruel world."
        self.current_text_length = 0
        self.active = False
        self.char_duration = 0.05
        self.elapsed = 0.0

        self.dialog = TextNode(
            text = "",
            font_name = settings[Builtins.FONT_NAME],
            x = settings[Builtins.VIEW_WIDTH] / 2,
            y = 16,
            scaling = scaling,
            font_size = 6,
            batch = batch
        )

    def update(self, dt: int) -> None:
        if self.active:
            self.elapsed += dt
            if self.elapsed >= self.char_duration:
                self.elapsed = 0.0
                self.current_text_length += 1
                if self.current_text_length >= len(self.on_text):
                    self.current_text_length = len(self.on_text)
        else:
            self.current_text_length = 0

        self.dialog.set_text(self.on_text[0:self.current_text_length])

    def delete(self) -> None:
        self.dialog.delete()

    def enable(self, active: bool):
        self.active = active