from typing import Callable, List, Optional
import pyglet

from engine.node import Node
from engine.settings import settings, Builtins
from engine.text_node import TextNode

class InteractionNode(Node):
    """
    Grabbable item.
    """

    def __init__(
        self,
        on_toggle: Optional[Callable[[], None]] = None,
        on_interaction: Optional[Callable[[bool], None]] = None
    ) -> None:
        super().__init__()

        self.enabled = False

        self.on_toggle = on_toggle
        self.on_interaction = on_interaction

    def toggle(self, enable: bool):
        """
        Activates or deactivates the interaction.
        """
        self.enabled = enable

        if self.on_toggle is not None:
            self.on_toggle(enable)

    def interact(self):
        """
        Interaction method.
        """

        if self.on_interaction is not None:
            self.on_interaction()


class DialogNode(InteractionNode):
    """
    Dialog handler.
    """
    def __init__(
        self,
        lines: Optional[List[str]] = None,
        # Character duration in seconds.
        char_duration: float = 0.05,
        scaling: int = 1,
        batch: Optional[pyglet.graphics.Batch] = None,
    ) -> None:
        super().__init__()

        self.lines = lines if lines is not None else []
        self.current_char = 0
        self.current_line = 0

        self.enabled = False
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
        if self.enabled:
            self.elapsed += dt
            if self.elapsed >= self.char_duration:
                self.elapsed = 0.0
                self.current_char += 1
                if self.current_char >= len(self.lines[self.current_line]):
                    self.current_char = len(self.lines[self.current_line])
        else:
            self.current_line = 0
            self.current_char = 0

        text = f"{self.lines[self.current_line][0:self.current_char]}"
        if self.current_char >= len(self.lines[self.current_line]) and self.current_line < len(self.lines) - 1:
            text += " ..."

        self.dialog.set_text(text)

    def delete(self) -> None:
        self.dialog.delete()

    def interact(self):
        """
        Progresses the dialog to the next line.
        """
        if self.enabled:
            if self.current_char < len(self.lines[self.current_line]) - 1:
                # Just go to end of the line if not there yet.
                self.current_char = len(self.lines[self.current_line]) - 1
            else:
                if self.current_line < len(self.lines) - 1:
                    # Go to next line if active and not there yet.
                    self.current_line += 1
                    self.current_char = 0
                else:
                    # End the dialog if finish line is reached already.
                    self.current_line = 0
                    self.current_char = 0
                    self.enabled = False
        else:
            # Reopen if not already.
            self.enabled = True