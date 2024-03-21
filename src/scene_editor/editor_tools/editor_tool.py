from typing import Callable, Optional, Tuple
import pyglet

from engine.collision.collision_node import SENSOR_COLOR
from engine.node import Node, PositionNode
from engine.shapes.rect_node import RectNode

class EditorTool(Node):
    def __init__(
        self,
        on_icon_changed: Optional[Callable] = None
    ) -> None:
        self.on_icon_changed: Optional[Callable] = on_icon_changed

        # Menu opening flag.
        self.menu_open: bool = False

        # Alternate activation flag.
        self.alt_mode: bool = False

        # Current cursor position.
        self.cursor_position: Tuple[int, int] = (0, 0)
        
        self.name: str = ""
        self.color: Tuple[int, int, int, int] = (0x00, 0x00, 0x00, 0xFF)

    def get_cursor_icon(self) -> PositionNode:
        """
        Generates and returns a cursor icon.
        """

        return PositionNode()

    def run(self, position: Tuple[int, int]) -> None:
        """
        Runs the tool on the currently specified tile position.
        """

    def toggle_menu(self, toggle: bool) -> None:
        """
        Toggles the tool's dedicated configuration interface.
        """

        self.menu_open = toggle

    def toggle_alt_mode(self, toggle: bool) -> None:
        """
        Toggles the tool's alternate mode.
        """

        self.alt_mode = toggle

    def move_cursor(self, position: Tuple[int, int]) -> None:
        """
        Notify the tool about the current cursor position.
        """

        self.cursor_position = position

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
        super().__init__()

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