from enum import Enum
from typing import Callable, Dict, List, Optional, Set, Tuple
import pyglet

from engine.collision.collision_node import COLLIDER_COLOR, SENSOR_COLOR
from engine.node import Node, PositionNode
from engine.shapes.rect_node import RectNode

class EditorToolKey(str, Enum):
    """
    All possible editor tool keys.
    """

    PLACE_PROP = "PLCPRP"
    PLACE_WALL = "PLCWLL"
    PLACE_DOOR = "PLCDOR"
    CLEAR = "CLR"

class EditorTool(Node):
    def __init__(
        self,
        batch: Optional[pyglet.graphics.Batch] = None
    ) -> None:
        # Tells whether
        self.config_open: bool = False
        
        self.name: str = ""
        self.color: Tuple[int, int, int, int] = (0x00, 0x00, 0x00, 0xFF)

        self.cursor_icon: PositionNode = RectNode(
            x = 0.0,
            y = 0.0,
            width = 100,
            height = 100,
            anchor_x = 50.0,
            anchor_y = 50.0,
            color = (0x33, 0xFF, 0x33, 0x7F),
            batch = batch
        )

    def toggle_menu(self, toggle: bool) -> None:
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
    def __init__(
        self,
        tile_size: Tuple[int, int],
        batch: Optional[pyglet.graphics.Batch] = None
    ) -> None:
        super().__init__(batch)

        self.name = "Place wall"
        self.color = COLLIDER_COLOR
        self.cursor_icon = RectNode(
            x = 0.0,
            y = 0.0,
            width = tile_size,
            height = tile_size,
            anchor_x = tile_size / 2,
            anchor_y = tile_size / 2,
            color = COLLIDER_COLOR,
            batch = batch
        )

    def toggle_menu(self, toggle: bool) -> None:
        return super().toggle_menu(toggle = toggle)

    def run(self, position: Tuple[int, int]) -> None:
        return super().run(position = position)

class PlaceDoorTool(EditorTool):
    def __init__(
        self,
        tile_size: Tuple[int, int],
        batch: Optional[pyglet.graphics.Batch] = None
    ) -> None:
        super().__init__(batch)

        self.name = "Place door"
        self.color = SENSOR_COLOR
        self.cursor_icon = RectNode(
            x = 0.0,
            y = 0.0,
            width = tile_size,
            height = tile_size,
            anchor_x = tile_size / 2,
            anchor_y = tile_size / 2,
            color = SENSOR_COLOR,
            batch = batch
        )

    def toggle_menu(self, toggle: bool) -> None:
        return super().toggle_menu(toggle = toggle)

    def run(self, position: Tuple[int, int]) -> None:
        return super().run(position = position)

class ClearTool(EditorTool):
    def __init__(
        self,
        tile_size: Tuple[int, int],
        batch: Optional[pyglet.graphics.Batch] = None
    ) -> None:
        super().__init__(batch)

        self.name = "Clear"
        self.color = (0xFF, 0x00, 0x00, 0xAA)
        self.cursor_icon = RectNode(
            x = 0.0,
            y = 0.0,
            width = tile_size,
            height = tile_size,
            anchor_x = tile_size / 2,
            anchor_y = tile_size / 2,
            color = (0xFF, 0x33, 0x33, 0x7F),
            batch = batch
        )

    def toggle_menu(self, toggle: bool) -> None:
        return super().toggle_menu(toggle = toggle)

    def run(self, position: Tuple[int, int]) -> None:
        return super().run(position = position)