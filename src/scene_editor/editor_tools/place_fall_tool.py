from typing import Callable
import pyglet

from constants import collision_tags, scenes
from amonite import controllers
from amonite.fall_node import FALL_COLOR, FallNode
from amonite.node import Node, PositionNode
from amonite.shapes.rect_node import RectNode
from editor_tools.editor_tool import EditorTool
from amonite.text_node import TextNode
from amonite.utils.utils import point_in_rect
from falls_loader import FallsLoader

TOOL_COLOR: tuple[int, int, int, int] = FALL_COLOR
ALT_COLOR: tuple[int, int, int, int] = (0x00, 0x44, 0xFF, 0x7F)

class FallEditorMenuNode(Node):
    def __init__(
        self,
        fall_names: list[str],
        view_width: int,
        view_height: int,
        start_open: bool = False,
        batch: pyglet.graphics.Batch | None = None,
    ) -> None:
        super().__init__()

        self.__fall_names = fall_names
        self.__view_width = view_width
        self.__view_height = view_height
        self.__batch = batch

        # Flag, defines whether the menu is open or close.
        self.__open = start_open

        # Elements in the current page.
        self.__fall_texts: list[TextNode] = []

        # Currently selected element.
        self.__current_fall_index: int = 0

        self.__background: RectNode | None = None

    def update(self, dt: int) -> None:
        super().update(dt)

        if self.__open:
            # Only handle controls if open:
            # Fall selection.
            self.__current_fall_index -= controllers.INPUT_CONTROLLER.old_get_cursor_movement_vec().y
            if self.__current_fall_index < 0:
                self.__current_fall_index = 0
            if self.__current_fall_index >= len(self.__fall_names[list(self.__fall_names.keys())[self.__current_page_index]]):
                self.__current_fall_index = len(self.__fall_names[list(self.__fall_names.keys())[self.__current_page_index]]) - 1

    def get_current_prop(self) -> str:
        return self.__fall_names[list(self.__fall_names.keys())[self.__current_page_index]][self.__current_fall_index]

    def is_open(self) -> bool:
        return self.__open

    def open(self) -> None:
        self.__open = True

        self.__background = RectNode(
            x = 0.0,
            y = 0.0,
            z = -100.0,
            width = self.__view_width,
            height = self.__view_height,
            color = (0x33, 0x33, 0x33),
            batch = self.__batch
        )
        self.__background.set_opacity(0xDD)

    def close(self) -> None:
        self.__open = False

        if self.__background is not None:
            self.__background.delete()
            self.__background = None

class PlaceFallTool(EditorTool):
    def __init__(
        self,
        view_width: int,
        view_height: int,
        tile_size: tuple[int, int],
        scene_name: str,
        on_icon_changed: Callable | None = None,
        world_batch: pyglet.graphics.Batch | None = None,
        ui_batch: pyglet.graphics.Batch | None = None
    ) -> None:
        super().__init__(
            on_icon_changed = on_icon_changed
        )

        # Parent overrides.
        self.name = "Place fall"
        self.color = TOOL_COLOR

        # Save data for later use.
        self.__tile_size: tuple[int, int] = tile_size
        self.__scene_name: str = scene_name
        self.__world_batch: pyglet.graphics.Batch | None = world_batch
        self.__ui_batch: pyglet.graphics.Batch | None = ui_batch

        # Create a menu to handle fall type selection.
        self.__menu = FallEditorMenuNode(
            fall_names = [],
            view_width = view_width,
            view_height = view_height,
            batch = ui_batch
        )

        # Area of the currently created
        self.__current_fall: RectNode | None = None

        # list of all inserted nodes.
        self.__falls: list[FallNode] = []
        self.__load_falls()

        # Starting position of the fall currently being placed.
        self.__starting_position: tuple[int, int] | None = None

    def move_cursor(self, map_position: tuple[int, int]) -> None:
        super().move_cursor(map_position)

        if self.__current_fall is not None and self.__starting_position is not None:
            # current_bounds: tuple[float, float, float, float] = self.__current_fall.get_bounds()
            self.__current_fall.set_bounds(
                bounds = (
                    # X position.
                    min(map_position[0], self.__starting_position[0]) * self.__tile_size[0],
                    # Y position.
                    min(map_position[1], self.__starting_position[1]) * self.__tile_size[1],
                    # Width.
                    (abs(map_position[0] - self.__starting_position[0]) + 1.0) * self.__tile_size[0],
                    # Height.
                    (abs(map_position[1] - self.__starting_position[1]) + 1.0) * self.__tile_size[1]
                )
            )

    def get_cursor_icon(self) -> PositionNode:
        # Return a tile-sized rectangle. It's color depends on whether alternate mode is on or off.
        return RectNode(
            x = 0.0,
            y = 0.0,
            width = self.__tile_size[0],
            height = self.__tile_size[1],
            anchor_x = self.__tile_size[0] / 2,
            anchor_y = self.__tile_size[1] / 2,
            color = ALT_COLOR if self.alt_mode else self.color,
            batch = self.__world_batch
        )

    def toggle_menu(self, toggle: bool) -> None:
        return super().toggle_menu(toggle = toggle)

    def toggle_alt_mode(self, toggle: bool) -> None:
        super().toggle_alt_mode(toggle)

        # Notify icon changed.
        if self.on_icon_changed is not None:
            self.on_icon_changed()

    def run(self, map_position: tuple[int, int]) -> None:
        super().run(map_position = map_position)

        if self.alt_mode:
            self.clear(map_position = map_position)
        else:
            if self.__starting_position == None:
                # Record starting position.
                self.__starting_position = map_position

                # Create the rect node for displaying the area currently being defined.
                self.__current_fall = RectNode(
                    x = map_position[0] * self.__tile_size[0],
                    y = map_position[1] * self.__tile_size[1],
                    width = self.__tile_size[0],
                    height = self.__tile_size[1],
                    color = FALL_COLOR,
                    batch = self.__world_batch,
                )
            else:
                # Just return if there's no current fall.
                if self.__current_fall is None:
                    return

                # Create a fall with the given position and size.
                # The fall size is computed by subtracting the start position from the current.
                current_bounds: tuple[float, float, float, float] = self.__current_fall.get_bounds()
                fall: FallNode = FallNode(
                    x = current_bounds[0],
                    y = current_bounds[1],
                    width = int(current_bounds[2]),
                    height = int(current_bounds[3]),
                    tags = [collision_tags.FALL],
                    batch = self.__world_batch
                )

                # Save the newly created fall
                self.__falls.append(fall)

                uniques.ACTIVE_SCENE.add_child(fall)

                # Reset the starting position.
                self.__starting_position = None

                # Delete the current fall.
                if self.__current_fall is not None:
                    self.__current_fall.delete()
                    self.__current_fall = None

        # Store the updated falls.
        FallsLoader.store(
            dest = f"{pyglet.resource.path[0]}/fallmaps/{self.__scene_name}.json",
            falls = self.__falls
        )

    def clear(self, map_position: tuple[int, int]) -> None:
        """
        Deletes any fall overlapping the provided map position, regardless of the selected fall tags.
        """

        # Delete the current fall if any.
        if self.__current_fall is not None:
            self.__current_fall.delete()
            self.__current_fall = None
            self.__starting_position = None
        else:
            # Define a test position at the center of a tile.
            test_position: tuple[float, float] = (
                map_position[0] * self.__tile_size[0] + self.__tile_size[0] / 2,
                map_position[1] * self.__tile_size[1] + self.__tile_size[1] / 2
            )

            # Filter overlapping falls.
            hit_falls: list[FallNode] = filter(
                lambda fall: point_in_rect(
                    test = test_position,
                    rect_position = (fall.x, fall.y),
                    rect_size = (fall.width, fall.height)
                ),
                self.__falls
            )

            # Delete any fall overlapping the current map_position.
            for fall in hit_falls:
                self.__falls.remove(fall)
                fall.delete()

    def __load_falls(self) -> None:
        # Delete all existing falls.
        for fall in self.__falls:
            if fall is not None:
                fall.delete()
        self.__falls.clear()

        # Recreate all of them from fallmap files.
        self.__falls = FallsLoader.fetch(
            source = f"fallmaps/{self.__scene_name}.json",
            batch = self.__world_batch
        )