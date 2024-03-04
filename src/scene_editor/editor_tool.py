from enum import Enum
from typing import Callable, Dict, List, Optional, Set, Tuple

class EditorToolKey(str, Enum):
    """
    All possible editor tool keys.
    """

    PLACE_PROP = "PLCPRP"
    PLACE_WALL = "PLCWLL"
    PLACE_DOOR = "PLCDOR"
    CLEAR = "CLR"

class EditorTool:
    def __init__(self) -> None:
        pass

    def open_config(self) -> None:
        """
        Opens the tool's dedicated configuration interface.
        """

        pass

class PlacePropTool(EditorTool):
    def open_config(self) -> None:
        return super().open_config()

class PlaceWallTool(EditorTool):
    def open_config(self) -> None:
        return super().open_config()

class PlaceDoorTool(EditorTool):
    def open_config(self) -> None:
        return super().open_config()

class ClearTool(EditorTool):
    def open_config(self) -> None:
        return super().open_config()

# All tools are in this dictionary.
tools: Dict[EditorToolKey, EditorTool] = {
    EditorToolKey.PLACE_PROP: PlacePropTool(),
    EditorToolKey.PLACE_WALL: PlaceWallTool(),
    EditorToolKey.PLACE_DOOR: PlaceDoorTool(),
    EditorToolKey.CLEAR: ClearTool()
}