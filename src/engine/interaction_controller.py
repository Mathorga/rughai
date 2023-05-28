from typing import List

from engine.interaction_node import InteractionNode


class InteractionController:
    def __init__(self) -> None:
        self.interactions: List[InteractionNode] = []
        self.active_interaction: InteractionNode

    def add_interaction(
        self,
        dialog: InteractionNode
    ) -> None:
        self.interactions.append(dialog)

    def toggle_interaction(
        self,
        dialog: InteractionNode,
        enable: bool
    ) -> None:
        # Make sure the dialog is already in the list.
        assert dialog in self.interactions

        if enable:
            self.active_interaction = dialog
        else:
            self.active_interaction = None

        dialog.toggle(enable = enable)

    def interact(self) -> None:
        if self.active_interaction is not None:
            self.active_interaction.interact()

    def remove_interactor(self, interactor: InteractionNode) -> None:
        if interactor == self.active_interaction:
            self.active_interaction = None

        self.interactions.remove(interactor)