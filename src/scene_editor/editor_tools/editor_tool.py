from enum import Enum
from typing import Callable, Dict, List, Optional, Set, Tuple

from scene_editor.editor_tools.place_prop_tool import PlacePropTool

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

    def run(self, position: Tuple[int, int]) -> None:
        """
        Runs the tool on the currently specified tile position.
        """

class PlaceWallTool(EditorTool):
    def open_config(self) -> None:
        return super().open_config()

    def run(self, position: Tuple[int, int]) -> None:
        return super().run()

class PlaceDoorTool(EditorTool):
    def open_config(self) -> None:
        return super().open_config()

    def run(self, position: Tuple[int, int]) -> None:
        return super().run()

class ClearTool(EditorTool):
    def open_config(self) -> None:
        return super().open_config()

    def run(self, position: Tuple[int, int]) -> None:
        return super().run()

# All tools are in this dictionary.
tools: Dict[EditorToolKey, EditorTool] = {
    EditorToolKey.PLACE_PROP: PlacePropTool(),
    EditorToolKey.PLACE_WALL: PlaceWallTool(),
    EditorToolKey.PLACE_DOOR: PlaceDoorTool(),
    EditorToolKey.CLEAR: ClearTool()
}