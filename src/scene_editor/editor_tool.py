from enum import Enum
from typing import Callable, Dict, List, Optional, Set, Tuple

class EditorAction(str, Enum):
    """
    All possible editor actions.
    """

    PLACE_PROP = "PLCPRP"
    PLACE_WALL = "PLCWLL"
    PLACE_DOOR = "PLCDOR"
    CLEAR = "CLR"

class EditorTool:
    def __init__(
        self,
        open_config: Optional[Callable[[None], None]] = None
    ) -> None:
        self.__open_config: Optional[Callable[[None], None]] = open_config

    def open_config(self):
        if self.__open_config is not None:
            self.__open_config()

# All tools are in this dictionary.
tools: Dict[EditorAction, EditorTool] = {
    EditorAction.PLACE_PROP: EditorTool(),
    EditorAction.PLACE_WALL: EditorTool(),
    EditorAction.PLACE_DOOR: EditorTool(),
    EditorAction.CLEAR: EditorTool()
}