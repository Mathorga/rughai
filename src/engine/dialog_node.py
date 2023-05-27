from typing import List, Optional
import pyglet

from engine.node import PositionNode
from engine.settings import settings, Builtins
from engine.text_node import TextNode


class DialogNode(PositionNode):
    def __init__(
        self,
        x: float = 0.0,
        y: float = 0.0,
        text: str = "hello_world",
        lines: Optional[List[str]] = None,
        # Character duration in seconds.
        char_duration: float = 0.05,
        scaling: int = 1,
        batch: Optional[pyglet.graphics.Batch] = None,
    ) -> None:
        super().__init__(x, y)

        self.lines = lines if lines is not None else []
        self.current_line = 0

        self.text = text
        self.current_text_length = 0
        self.active = False
        self.char_duration = char_duration
        self.elapsed = 0.0

        self.dialog = TextNode(
            # Start with no text.
            text = "",
            font_name = settings[Builtins.FONT_NAME],
            x = settings[Builtins.VIEW_WIDTH] / 2,
            y = 16,
            width = settings[Builtins.VIEW_WIDTH] * 0.8,
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
                if self.current_text_length >= len(self.text):
                    self.current_text_length = len(self.text)
        else:
            self.current_text_length = 0

        self.dialog.set_text(self.lines[self.current_line][0:self.current_text_length])

    def delete(self) -> None:
        self.dialog.delete()

    def enable(self, active: bool):
        """
        Activates or deactivates the dialog.
        If active is True, then the dialog starts from the beginning.
        """
        self.active = active

    def next_line(self):
        """
        Progresses the dialog to the next line.
        """
        self.current_line += 1