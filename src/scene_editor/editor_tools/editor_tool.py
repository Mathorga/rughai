from enum import Enum
from typing import Callable, Dict, List, Optional, Set, Tuple

from engine.node import Node, PositionNode

class EditorToolKey(str, Enum):
    """
    All possible editor tool keys.
    """

    PLACE_PROP = "PLCPRP"
    PLACE_WALL = "PLCWLL"
    PLACE_DOOR = "PLCDOR"
    CLEAR = "CLR"

class EditorTool(Node):
    def __init__(self) -> None:
        # Tells whether
        self.config_open: bool = False

        self.cursor_icon: PositionNode = PositionNode()

    def toggle_config(self, toggle: bool) -> None:
        """
        Toggles the tool's dedicated configuration interface.
        """

        self.config_open = toggle

    def run(self, position: Tuple[int, int]) -> None:
        """
        Runs the tool on the currently specified tile position.
        """

    def undo(self) -> None:
        """
        Undoes the latest run.
        """

    def redo(self) -> None:
        """
        Redoes the latest run.
        """

class PlaceWallTool(EditorTool):
    def toggle_config(self) -> None:
        return super().toggle_config()

    def run(self, position: Tuple[int, int]) -> None:
        return super().run(position = position)

class PlaceDoorTool(EditorTool):
    def toggle_config(self) -> None:
        return super().toggle_config()

    def run(self, position: Tuple[int, int]) -> None:
        return super().run(position = position)

class ClearTool(EditorTool):
    def toggle_config(self) -> None:
        return super().toggle_config()

    def run(self, position: Tuple[int, int]) -> None:
        return super().run(position = position)