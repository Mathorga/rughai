from typing import Callable, Dict, List, Optional, Tuple
import pyglet

from constants import collision_tags, scenes
from engine import controllers
from engine.collision.collision_node import COLLIDER_COLOR
from engine.node import Node, PositionNode
from engine.settings import SETTINGS, Keys
from engine.shapes.rect_node import RectNode
from editor_tools.editor_tool import EditorTool
from engine.text_node import TextNode
from engine.utils.utils import point_in_rect
from engine.wall_node import WALL_COLOR, WallNode
from walls_loader import WallsLoader

TOOL_COLOR: Tuple[int, int, int, int] = WALL_COLOR
ALT_COLOR: Tuple[int, int, int, int] = (0xFF, 0x7F, 0x00, 0x7F)

class WallEditorMenuNode(Node):
    def __init__(
        self,
        wall_names: List[str],
        view_width: int,
        view_height: int,
        start_open: bool = False,
        batch: Optional[pyglet.graphics.Batch] = None,
    ) -> None:
        super().__init__()

        self.__prop_names = wall_names
        self.__view_width = view_width
        self.__view_height = view_height
        self.__batch = batch

        # Flag, defines whether the menu is open or close.
        self.__open = start_open

        # Elements in the current page.
        self.__wall_texts: List[TextNode] = []

        # Currently selected element.
        self.__current_wall_index: int = 0

        self.__background: Optional[RectNode] = None

    def update(self, dt: int) -> None:
        super().update(dt)

        if self.__open:
            # Only handle controls if open:
            # Wall selection.
            self.__current_wall_index -= controllers.INPUT_CONTROLLER.get_cursor_movement().y
            if self.__current_wall_index < 0:
                self.__current_wall_index = 0
            if self.__current_wall_index >= len(self.__prop_names[list(self.__prop_names.keys())[self.__current_page_index]]):
                self.__current_wall_index = len(self.__prop_names[list(self.__prop_names.keys())[self.__current_page_index]]) - 1

    def get_current_prop(self) -> str:
        return self.__prop_names[list(self.__prop_names.keys())[self.__current_page_index]][self.__current_wall_index]

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

class PlaceWallTool(EditorTool):
    def __init__(
        self,
        view_width: int,
        view_height: int,
        tile_size: Tuple[int, int],
        scene_name: str,
        on_icon_changed: Optional[Callable] = None,
        world_batch: Optional[pyglet.graphics.Batch] = None,
        ui_batch: Optional[pyglet.graphics.Batch] = None
    ) -> None:
        super().__init__(
            on_icon_changed = on_icon_changed
        )

        # Parent overrides.
        self.name = "Place wall"
        self.color = TOOL_COLOR

        # Save data for later use.
        self.__tile_size: Tuple[int, int] = tile_size
        self.__scene_name: str = scene_name
        self.__world_batch: Optional[pyglet.graphics.Batch] = world_batch
        self.__ui_batch: Optional[pyglet.graphics.Batch] = ui_batch

        # Create a menu to handle wall type selection.
        self.__menu = WallEditorMenuNode(
            wall_names = [],
            view_width = view_width,
            view_height = view_height,
            batch = ui_batch
        )

        # Area of the currently created
        self.__current_wall: Optional[RectNode] = None

        # List of all inserted nodes.
        self.__walls: List[WallNode] = []
        self.__load_walls()

        # Starting position of the wall currently being placed.
        self.__starting_position: Optional[Tuple[int, int]] = None

    def move_cursor(self, map_position: Tuple[int, int]) -> None:
        super().move_cursor(map_position)

        if self.__current_wall is not None and self.__starting_position is not None:
            # current_bounds: Tuple[float, float, float, float] = self.__current_wall.get_bounds()
            self.__current_wall.set_bounds(
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

    def run(self, map_position: Tuple[int, int]) -> None:
        super().run(map_position = map_position)

        if self.alt_mode:
            self.clear(map_position = map_position)
        else:
            if self.__starting_position == None:
                # Record starting position.
                self.__starting_position = map_position

                # Create the rect node for displaying the area currently being defined.
                self.__current_wall = RectNode(
                    x = map_position[0] * self.__tile_size[0],
                    y = map_position[1] * self.__tile_size[1],
                    width = self.__tile_size[0],
                    height = self.__tile_size[1],
                    color = WALL_COLOR,
                    batch = self.__world_batch,
                )
            else:
                # Just return if there's no current wall.
                if self.__current_wall is None:
                    return

                # Create a wall with the given position and size.
                # The wall size is computed by subtracting the start position from the current.
                current_bounds: Tuple[float, float, float, float] = self.__current_wall.get_bounds()
                wall: WallNode = WallNode(
                    x = current_bounds[0],
                    y = current_bounds[1],
                    width = int(current_bounds[2]),
                    height = int(current_bounds[3]),
                    tags = [collision_tags.PLAYER_COLLISION],
                    batch = self.__world_batch
                )

                # Save the newly created wall
                self.__walls.append(wall)

                scenes.ACTIVE_SCENE.add_child(wall)

                # Reset the starting position.
                self.__starting_position = None

                # Delete the current wall.
                if self.__current_wall is not None:
                    self.__current_wall.delete()
                    self.__current_wall = None

        # Store the updated walls.
        WallsLoader.store(
            dest = f"{pyglet.resource.path[0]}/wallmaps/{self.__scene_name}.json",
            walls = self.__walls
        )

    def clear(self, map_position: Tuple[int, int]) -> None:
        """
        Deletes any wall overlapping the provided map position, regardless of the selected wall tags.
        """

        # Delete the current wall if any.
        if self.__current_wall is not None:
            self.__current_wall.delete()
            self.__current_wall = None
            self.__starting_position = None
        else:
            # Define a test position at the center of a tile.
            test_position: Tuple[float, float] = (
                map_position[0] * self.__tile_size[0] + self.__tile_size[0] / 2,
                map_position[1] * self.__tile_size[1] + self.__tile_size[1] / 2
            )

            # Filter overlapping walls.
            hit_walls: List[WallNode] = filter(
                lambda wall: point_in_rect(
                    test = test_position,
                    rect_position = (wall.x, wall.y),
                    rect_size = (wall.width, wall.height)
                ),
                self.__walls
            )

            # Delete any wall overlapping the current map_position.
            for wall in hit_walls:
                self.__walls.remove(wall)
                wall.delete()

    def __load_walls(self) -> None:
        # Delete all existing walls.
        for wall in self.__walls:
            if wall is not None:
                wall.delete()
        self.__walls.clear()

        # Recreate all of them from wallmap files.
        self.__walls = WallsLoader.fetch(
            source = f"wallmaps/{self.__scene_name}.json",
            batch = self.__world_batch
        )