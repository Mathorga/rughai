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

from scene_editor.editor_tools.editor_tool import EditorToolKey

class ActionSign(PositionNode):
    def __init__(
        self,
        x: float = 0.0,
        y: float = 0.0,
        action: EditorToolKey = EditorToolKey.PLACE_PROP,
        on_toggle: Optional[Callable[[EditorToolKey], None]] = None,
        batch: Optional[pyglet.graphics.Batch] = None
    ) -> None:
        super().__init__(
            x = x,
            y = y
        )

        self.__batch = batch
        self.__label: Optional[TextNode] = None

        self.action = action
        self.__on_toggle = on_toggle
        self.visible = True

    def __compute_text(self) -> str:
        return f"(tab) {self.action.value}"

    def __compute_color(self) -> Tuple[int, int, int, int]:
        return (0xFF, 0x00, 0x00, 0xFF) if self.action == EditorToolKey.CLEAR else (0x00, 0xFF, 0x00, 0xFF)

    def update(self, dt: int) -> None:
        super().update(dt)

        # Only do stuff if visible.
        if self.visible:
            if controllers.INPUT_CONTROLLER.get_switch():
                self.toggle()

    def toggle(self) -> None:
        if self.action == EditorToolKey.PLACE_PROP:
            self.action = EditorToolKey.CLEAR
        else:
            self.action = EditorToolKey.PLACE_PROP

        if self.__label is not None:
            self.__label.set_text(self.__compute_text())
            self.__label.set_color(self.__compute_color())

        # Toggle callback.
        if self.__on_toggle is not None:
            self.__on_toggle(self.action)

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
            on_toggle = self.__on_action_toggle,
            batch = self.__scene.ui_batch
        )
        self.__action_sign.show()

        # Fetch current prop maps.
        # self.__prop_sets = PropLoader.fetch_prop_sets(
        #     source = f"propmaps/{scene_name}"
        # )
        self.__prop_sets: List[Dict[str, Set[Tuple[int, int]]]] = [
            PropLoader.fetch_prop_sets(
                source = f"propmaps/{scene_name}"
            )
        ]
        self.__current_props_index = 0

        self.__props: List[PositionNode] = []
        self.__refresh_props()

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
        self.__scene.add_child(self.__menu)

    def draw(self) -> None:
        if self.__scene is not None:
            self.__scene.draw()

    def update(self, dt) -> None:
        if not self.__menu.is_open():
            if controllers.INPUT_CONTROLLER.get_sprint():
                # Clear history until the current index is reached.
                self.__prop_sets = self.__prop_sets[0:self.__current_props_index + 1]

                # Add an entry in the prop sets history.
                self.__prop_sets.append(copy.deepcopy(self.__prop_sets[self.__current_props_index]))

                prop_sets_size = len(self.__prop_sets)
                if prop_sets_size > 20:
                    self.__prop_sets = self.__prop_sets[prop_sets_size - 20:prop_sets_size]
                else:
                    self.__current_props_index += 1

                if self.__action_sign.action == EditorToolKey.PLACE_PROP:
                    # Add the currently selected prop if the interaction button was pressed.
                    if self.__menu.get_current_prop() not in list(self.__prop_sets[self.__current_props_index].keys()):
                        self.__prop_sets[self.__current_props_index][self.__menu.get_current_prop()] = set()
                    self.__prop_sets[self.__current_props_index][self.__menu.get_current_prop()].add(self.__cursor.get_map_position())
                else:
                    # Delete anything in the current map position, regardless of the selected prop.
                    for prop_set in list(self.__prop_sets[self.__current_props_index].values()):
                        prop_set.discard(self.__cursor.get_map_position())

                # Refresh props to apply changes.
                self.__refresh_props()
                PropLoader.save_prop_sets(
                    dest = f"{pyglet.resource.path[0]}/propmaps/{self.__scene_name}",
                    map_width = self.__tilemap_width,
                    map_height = self.__tilemap_height,
                    prop_sets = self.__prop_sets[self.__current_props_index]
                )

            if controllers.INPUT_CONTROLLER.get_redo():
                self.__current_props_index += 1
                if self.__current_props_index > len(self.__prop_sets) - 1:
                    self.__current_props_index = len(self.__prop_sets) - 1
                self.__refresh_props()
            elif controllers.INPUT_CONTROLLER.get_undo():
                self.__current_props_index -= 1
                if self.__current_props_index < 0:
                    self.__current_props_index = 0
                self.__refresh_props()

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

    def __refresh_props(self) -> None:
        # Delete all existing props.
        for prop in self.__props:
            if prop is not None:
                prop.delete()
        self.__props.clear()

        # Recreate all of them starting from prop maps.
        for prop_name in list(self.__prop_sets[self.__current_props_index].keys()):
            for position in self.__prop_sets[self.__current_props_index][prop_name]:
                prop = map_prop(
                    prop_name,
                    x = position[0] * self.__tile_size + self.__tile_size / 2,
                    y = position[1] * self.__tile_size + self.__tile_size / 2,
                    batch = self.__scene.world_batch
                )

                if prop is not None:
                    self.__props.append(prop)

    def __on_action_toggle(self, action: EditorToolKey) -> None:
        if action == EditorToolKey.CLEAR:
            self.__cursor.set_child(self.__get_del_cursor_child())
        else:
            cursor_icon = map_prop(
                self.__menu.get_current_prop(),
                x = self.__cursor.x,
                y = self.__cursor.y,
                batch = self.__scene.world_batch
            )

            if cursor_icon is not None:
                self.__cursor.set_child(cursor_icon)

    def __on_menu_open(self) -> None:
        self.__cursor.disable_controls()
        self.__action_sign.hide()

    def __on_menu_close(self) -> None:
        self.__cursor.enable_controls()
        self.__action_sign.show()

        if self.__action_sign.action == EditorToolKey.PLACE_PROP:
            cursor_icon = map_prop(
                self.__menu.get_current_prop(),
                x = self.__cursor.x,
                y = self.__cursor.y,
                batch = self.__scene.world_batch
            )

            if cursor_icon is not None:
                self.__cursor.set_child(cursor_icon)