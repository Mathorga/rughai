import copy
from enum import Enum
import json
from typing import Callable, Dict, List, Optional, Set, Tuple
import pyglet

from engine import controllers
from engine.prop_loader import PropLoader, map_prop
from engine.node import Node, PositionNode
from engine.scene_node import SceneNode
from engine.shapes.line_node import LineNode
from engine.shapes.rect_node import RectNode
from engine.text_node import TextNode
from engine.tilemap_node import TilemapNode
from engine.settings import SETTINGS, Keys
from engine.map_cursor_node import MapCursornode

from scene_editor.editor_tools.editor_tool import ClearTool, EditorTool, EditorToolKey, PlaceDoorTool, PlaceWallTool
from scene_editor.editor_tools.place_prop_tool import PlacePropTool

class ActionSign(PositionNode):
    def __init__(
        self,
        x: float = 0.0,
        y: float = 0.0,
        action: EditorToolKey = EditorToolKey.PLACE_PROP,
        batch: Optional[pyglet.graphics.Batch] = None
    ) -> None:
        super().__init__(
            x = x,
            y = y
        )

        self.__batch = batch
        self.__label: Optional[TextNode] = None

        self.action = action
        self.visible = True

    def __compute_text(self) -> str:
        return f"(tab) {self.action.value}"

    def __compute_color(self) -> Tuple[int, int, int, int]:
        return (0xFF, 0x00, 0x00, 0xFF) if self.action == EditorToolKey.CLEAR else (0x00, 0xFF, 0x00, 0xFF)

    def toggle(self) -> None:
        if self.action == EditorToolKey.PLACE_PROP:
            self.action = EditorToolKey.CLEAR
        else:
            self.action = EditorToolKey.PLACE_PROP

        if self.__label is not None:
            self.__label.set_text(self.__compute_text())
            self.__label.set_color(self.__compute_color())

    def hide(self) -> None:
        self.visible = False

        if self.__label is not None:
            self.__label.delete()
            self.__label = None

    def show(self) -> None:
        self.visible = True

        if self.__label is None:
            self.__label = TextNode(
                x = self.x,
                y = self.y,
                width = 0.0,
                anchor_x = "left",
                text = self.__compute_text(),
                color = self.__compute_color(),
                font_name = "rughai",
                multiline = False,
                batch = self.__batch
            )

class PropPlacementScene(Node):
    def __init__(
        self,
        window: pyglet.window.Window,
        view_width: int,
        view_height: int,
        scene_name: str,
        on_ended: Optional[Callable[[dict], None]] = None
    ):
        super().__init__()
        self.__window = window
        self.__on_ended = on_ended
        self.__scene_name = scene_name

        # Define the scene.
        self.__scene = SceneNode(
            window = window,
            view_width = view_width,
            view_height = view_height,
            default_cam_speed = SETTINGS[Keys.CAMERA_SPEED],
            title = scene_name
        )

        # Define a tilemap.
        tilemaps = TilemapNode.from_tmx_file(
            source = f"tilemaps/{scene_name}.tmx",
            batch = self.__scene.world_batch
        )
        self.__tile_size = tilemaps[0].get_tile_size()[0]
        self.__tilemap_width = tilemaps[0].map_width
        self.__tilemap_height = tilemaps[0].map_height
        cam_bounds = tilemaps[0].bounds

        # Editor tool.
        self.__current_tool: int = 0

        # All tools are in this dictionary.
        self.__tools: List[EditorTool] = [
            PlacePropTool(
                view_width = view_width,
                view_height = view_height,
                scene_name = scene_name
            ),
            PlaceWallTool(),
            PlaceDoorTool(),
            ClearTool()
        ]

        # Defines whether the current tool's config is open or not.
        self.__config_open: bool = False

        # Cursor.
        cursor_position = (
            (self.__tilemap_width / 2) * self.__tile_size,
            (self.__tilemap_height / 2) * self.__tile_size
        )

        # "Delete action" cursor child.
        cam_target = PositionNode()
        self.__cursor = MapCursornode(
            tile_width = self.__tile_size,
            tile_height = self.__tile_size,
            child = self.__get_del_cursor_child(),
            cam_target = cam_target,
            x = cursor_position[0] + self.__tile_size / 2,
            y = cursor_position[1] + self.__tile_size / 2
        )

        # Action sign.
        self.__action_sign = ActionSign(
            x = self.__tile_size,
            y = view_height - self.__tile_size,
            action = EditorToolKey.CLEAR,
            batch = self.__scene.ui_batch
        )
        self.__action_sign.show()

        self.__bound_lines = [
            LineNode(
                x = 0.0,
                y = 0.0,
                delta_x = (self.__tilemap_width) * self.__tile_size,
                delta_y = 0.0,
                color = (0xFF, 0x33, 0x00, 0x7F),
                batch = self.__scene.world_batch
            ),
            LineNode(
                x = self.__tilemap_width * self.__tile_size,
                y = 0.0,
                delta_x = 0.0,
                delta_y = self.__tilemap_height * self.__tile_size,
                color = (0xFF, 0x33, 0x00, 0x7F),
                batch = self.__scene.world_batch
            ),
            LineNode(
                x = 0.0,
                y = self.__tilemap_height * self.__tile_size,
                delta_x = self.__tilemap_width * self.__tile_size,
                delta_y = 0.0,
                color = (0xFF, 0x33, 0x00, 0x7F),
                batch = self.__scene.world_batch
            ),
            LineNode(
                x = 0.0,
                y = 0.0,
                delta_x = 0.0,
                delta_y = self.__tilemap_height * self.__tile_size,
                color = (0xFF, 0x33, 0x00, 0x7F),
                batch = self.__scene.world_batch
            )
        ]

        self.__scene.add_children(tilemaps)
        self.__scene.add_child(cam_target, cam_target = True)
        self.__scene.add_child(self.__action_sign)
        self.__scene.add_child(self.__cursor)

    def draw(self) -> None:
        if self.__scene is not None:
            self.__scene.draw()

    def update(self, dt) -> None:
        # Toggle open/close upon start key pressed.
        if controllers.INPUT_CONTROLLER.get_start():
            self.__toggle_config()

        if self.__config_open:
            if controllers.INPUT_CONTROLLER.get_switch():
                # Switch action.
                self.__current_tool += 1
                self.__current_tool %= len(self.__tools)

                self.__cursor.set_child(self.__tools[self.__current_tool].cursor_icon)

            if controllers.INPUT_CONTROLLER.get_sprint():
                self.__tools[self.__current_tool].run()

            if controllers.INPUT_CONTROLLER.get_redo():
                self.__tools[self.__current_tool].redo()
            elif controllers.INPUT_CONTROLLER.get_undo():
                self.__tools[self.__current_tool].undo()
        else:
            if self.__scene is not None:
                self.__scene.update(dt)

    def delete(self) -> None:
        if self.__scene is not None:
            self.__scene.delete()

    def __get_del_cursor_child(self) -> PositionNode:
        return RectNode(
            x = 0.0,
            y = 0.0,
            width = self.__tile_size,
            height = self.__tile_size,
            anchor_x = self.__tile_size / 2,
            anchor_y = self.__tile_size / 2,
            color = (0xFF, 0x33, 0x33, 0x7F),
            batch = self.__scene.world_batch
        )

    def __toggle_config(self) -> None:
        self.__config_open = not self.__config_open

        if self.__config_open:
            self.__cursor.disable_controls()
            self.__action_sign.hide()
        else:
            self.__cursor.enable_controls()
            self.__action_sign.show()

        # Toggle the current tool.
        self.__tools[self.__current_tool].toggle_config(self.__config_open)