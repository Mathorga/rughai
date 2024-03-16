from typing import Dict, List, Optional, Tuple
import pyglet

from constants import collision_tags, scenes
from engine import controllers
from engine.collision.collision_node import COLLIDER_COLOR
from engine.node import Node, PositionNode
from engine.shapes.rect_node import RectNode
from editor_tools.editor_tool import EditorTool
from engine.text_node import TextNode
from engine.wall_node import WallNode

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
        self.__current_prop_icon: Optional[SpriteNode] = None

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

    def get_current_image(self) -> pyglet.image.TextureRegion:
        current_prop_name = self.get_current_prop()
        icon = pyglet.resource.image(f"sprites/prop/{current_page_name}/{current_prop_name}/{current_prop_name}_icon.png")
        icon.anchor_x = icon.width / 2
        icon.anchor_y = icon.height / 2

        return icon

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
        batch: Optional[pyglet.graphics.Batch] = None
    ) -> None:
        super().__init__(batch)

        # Parent overrides.
        self.name = "Place wall"
        self.color = COLLIDER_COLOR

        # Save data for later use.
        self.__tile_size = tile_size
        self.__batch = batch

        # Create a menu to handle wall type selection.
        self.__menu = WallEditorMenuNode(
            wall_names = [],
            view_width = view_width,
            view_height = view_height,
            batch = batch
        )

        # List of all inserted nodes.
        self.__walls: List[WallNode] = []

        # Starting position of the wall currently being placed.
        self.__starting_position: Optional[Tuple[int, int]] = None

    def get_cursor_icon(self) -> PositionNode:
        return RectNode(
            x = 0.0,
            y = 0.0,
            width = self.__tile_size,
            height = self.__tile_size,
            anchor_x = self.__tile_size / 2,
            anchor_y = self.__tile_size / 2,
            color = COLLIDER_COLOR,
            batch = self.__batch
        )

    def update(self, dt: float) -> None:
        return super().update(dt)

    def toggle_menu(self, toggle: bool) -> None:
        return super().toggle_menu(toggle = toggle)

    def run(self, position: Tuple[int, int]) -> None:
        super().run(position = position)

        if self.__starting_position == None:
            # Record starting position.
            self.__starting_position = position
        else:
            # Create a wall with the given position and size.
            # The wall size is computed by subtracting the start position from the current.
            wall: WallNode = WallNode(
                x = self.__starting_position[0],
                y = self.__starting_position[1],
                width = position[0] - self.__starting_position[0],
                height = position[1] - self.__starting_position[1],
                tags = [collision_tags.PLAYER_COLLISION],
                batch = self.__batch
            )

            # Save the newly created wall
            self.__walls.append(wall)

            scenes.ACTIVE_SCENE.add_child(wall)

            # Reset the starting position.
            self.__starting_position = None