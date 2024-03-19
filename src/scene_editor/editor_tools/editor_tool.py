from enum import Enum
from typing import Callable, Dict, List, Optional, Set, Tuple
import pyglet

from engine.collision.collision_node import COLLIDER_COLOR, SENSOR_COLOR
from engine.node import Node, PositionNode
from engine.shapes.rect_node import RectNode

class EditorTool(Node):
    def __init__(
        self,
        batch: Optional[pyglet.graphics.Batch] = None
    ) -> None:
        # Menu opening flag.
        self.menu_open: bool = False

        # Alternate activation flag.
        self.alt_mode: bool = False
        
        self.name: str = ""
        self.color: Tuple[int, int, int, int] = (0x00, 0x00, 0x00, 0xFF)

    def get_cursor_icon(self) -> PositionNode:
        """
        Generates and returns a cursor icon.
        """

        return PositionNode()

    def toggle_menu(self, toggle: bool) -> None:
        """
        Toggles the tool's dedicated configuration interface.
        """

        self.menu_open = toggle

    def run(self, position: Tuple[int, int]) -> None:
        """
        Runs the tool on the currently specified tile position.
        """

    def toggle_alt_mode(self, toggle: bool) -> None:
        """
        Toggles the tool's alternate mode.
        """

        self.alt_mode = toggle

    def undo(self) -> None:
        """
        Undoes the latest run.
        """

    def redo(self) -> None:
        """
        Redoes the latest run.
        """

class PlaceDoorTool(EditorTool):
    def __init__(
        self,
        tile_size: Tuple[int, int],
        batch: Optional[pyglet.graphics.Batch] = None
    ) -> None:
        super().__init__(batch)

        self.name = "Place door"
        self.color = SENSOR_COLOR

        self.__tile_size = tile_size
        self.__batch = batch

    def get_cursor_icon(self) -> PositionNode:
        return RectNode(
            x = 0.0,
            y = 0.0,
            width = self.__tile_size,
            height = self.__tile_size,
            anchor_x = self.__tile_size / 2,
            anchor_y = self.__tile_size / 2,
            color = SENSOR_COLOR,
            batch = self.__batch
        )

    def toggle_menu(self, toggle: bool) -> None:
        return super().toggle_menu(toggle = toggle)

    def run(self, position: Tuple[int, int]) -> None:
        return super().run(position = position)