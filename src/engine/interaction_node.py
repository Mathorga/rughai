from typing import Callable, Optional

from engine.node import Node

class InteractionNode(Node):
    """
    Generic interactable.
    """

    def __init__(
        self,
        on_toggle: Optional[Callable[[bool], None]] = None,
        on_interaction: Optional[Callable[[], None]] = None
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