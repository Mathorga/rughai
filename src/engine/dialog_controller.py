from typing import List

from engine.dialog_node import DialogNode


class DialogController:
    def __init__(self) -> None:
        self.dialogs: List[DialogNode] = []

    def add_dialog(
        self,
        dialog: DialogNode
    ) -> None:
        self.dialogs.append(dialog)

    def next_line(self) -> None:
        for dialog in self.dialogs:
            dialog.next_line()