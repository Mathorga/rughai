from typing import List

from engine.dialog_node import DialogNode


class DialogController:
    def __init__(self) -> None:
        self.dialogs: List[DialogNode] = []
        self.active_dialog: DialogNode

    def add_dialog(
        self,
        dialog: DialogNode
    ) -> None:
        self.dialogs.append(dialog)

    def toggle_dialog(
        self,
        dialog: DialogNode,
        enable: bool
    ) -> None:
        # Make sure the dialog is already in the list.
        assert dialog in self.dialogs

        if enable:
            self.active_dialog = dialog
        else:
            self.active_dialog = None

        dialog.toggle(enable = enable)

    def next_line(self) -> None:
        if self.active_dialog is not None:
            self.active_dialog.next_line()