from enum import Enum
import json
import os
from turtle import width
from typing import Callable, Dict, List, Optional, Text, Tuple
import pyglet
from engine import controllers

from engine.prop_loader import PropLoader, map_prop
from engine.node import Node, PositionNode
from engine.scene_node import SceneNode
from engine.shapes.rect_node import RectNode
from engine.sprite_node import SpriteNode
from engine.text_node import TextNode
from engine.tilemap_node import TilemapNode
from engine.settings import SETTINGS, Builtins

from clouds_node import CloudsNode
from map_cursor_node import MapCursornode

class EditorAction(str, Enum):
    # Settings.
    INSERT = "INS"
    DELETE = "DEL"

class ActionSign(PositionNode):
    def __init__(
        self,
        x: float = 0.0,
        y: float = 0.0,
        action: EditorAction = EditorAction.INSERT,
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
        return (0xFF, 0x00, 0x00, 0xFF) if self.action == EditorAction.DELETE else (0x00, 0xFF, 0x00, 0xFF)

    def update(self, dt: int) -> None:
        super().update(dt)

        # Only do stuff if visible.
        if self.visible:
            if controllers.INPUT_CONTROLLER.get_switch():
                self.toggle()

    def toggle(self) -> None:
        if self.action == EditorAction.INSERT:
            self.action = EditorAction.DELETE
        else:
            self.action = EditorAction.INSERT

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

class EditorMenuEntryNode(PositionNode):
    def __init__(
        self,
        x: float = 0.0,
        y: float = 0.0,
        z: float = 0.0
    ) -> None:
        super().__init__(x, y, z)

class EditorMenuTitleNode(PositionNode):
    def __init__(
        self,
        text: str,
        view_width: int,
        view_height: int,
        z: float = 0.0,
        batch: Optional[pyglet.graphics.Batch] = None,
    ) -> None:
        super().__init__(
            view_width / 2,
            view_height - 10,
            z
        )

        self.__left_arrow = TextNode(
            x = self.x + 10,
            y = self.y,
            width = view_width,
            text = "< (Q/L)",
            align = "left",
            anchor_x = "center",
            font_name = "rughai",
            batch = batch
        )
        self.__text = TextNode(
            x = self.x,
            y = self.y,
            width = view_width,
            text = text,
            color = (0xFF, 0xFF, 0xFF, 0xFF),
            align = "center",
            anchor_x = "center",
            font_name = "rughai",
            batch = batch
        )
        self.__right_arrow = TextNode(
            x = self.x - 10,
            y = self.y,
            width = view_width,
            text = "(E/R) >",
            align = "right",
            anchor_x = "center",
            font_name = "rughai",
            batch = batch
        )

    def delete(self) -> None:
        if self.__text is not None:
            self.__text.delete()
            self.__text = None

class PropEditorMenuNode(Node):
    def __init__(
        self,
        prop_names: Dict[str, List[str]],
        view_width: int,
        view_height: int,
        open: bool = False,
        batch: Optional[pyglet.graphics.Batch] = None,
        on_open: Optional[Callable[[], None]] = None,
        on_close: Optional[Callable[[], None]] = None,
    ) -> None:
        super().__init__()

        self.__prop_names = prop_names
        self.__view_width = view_width
        self.__view_height = view_height
        self.__batch = batch

        # Flag, defines whether the menu is open or close.
        self.__open = open

        # Current page.
        self.__current_page: int = 0
        self.__page_title: Optional[EditorMenuTitleNode] = None

        # Elements in the current page.
        self.__prop_texts: List[TextNode] = []
        # self.__prop_icons: List[SpriteNode] = []

        # Currently selected element.
        self.__current_prop: int = 0
        self.__current_prop_icon: Optional[SpriteNode] = None

        # Open/close callbacks.
        self.__on_open = on_open
        self.__on_close = on_close

        self.__background: Optional[RectNode] = None

    def update(self, dt: int) -> None:
        super().update(dt)

        # Toggle open/close upon start key pressed.
        if controllers.INPUT_CONTROLLER.get_start():
            self.toggle()

        if self.__open:
            # Only handle all other controls if open:
            # Page change.
            if controllers.INPUT_CONTROLLER.get_menu_page_left():
                self.__current_page -= 1
                self.__current_page = self.__current_page % len(self.__prop_names)
            if controllers.INPUT_CONTROLLER.get_menu_page_right():
                self.__current_page += 1
                self.__current_page = self.__current_page % len(self.__prop_names)

            # Prop selection.
            self.__current_prop += controllers.INPUT_CONTROLLER.get_cursor_movement().x
            if self.__current_prop < 0:
                self.__current_prop = 0
            if self.__current_prop >= len(self.__prop_names[list(self.__prop_names.keys())[self.__current_page]]):
                self.__current_prop = len(self.__prop_names[list(self.__prop_names.keys())[self.__current_page]]) - 1

            self.set_page(list(self.__prop_names.keys())[self.__current_page])

    def get_current_page(self) -> str:
        return list(self.__prop_names.keys())[self.__current_page]

    def get_current_prop(self) -> str:
        return self.__prop_names[list(self.__prop_names.keys())[self.__current_page]][self.__current_prop]

    def is_open(self) -> bool:
        return self.__open
    
    def toggle(self) -> None:
        if self.__open:
            self.close()
        else:
            self.open()

    def open(self) -> None:
        self.__open = True

        self.set_page(list(self.__prop_names.keys())[self.__current_page])

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

        # Open callback.
        if self.__on_open is not None:
            self.__on_open()

    def close(self) -> None:
        self.__open = False

        self.clear_page()

        if self.__background is not None:
            self.__background.delete()
            self.__background = None

        # Close callback.
        if self.__on_close is not None:
            self.__on_close()

    def clear_page(self) -> None:
        # Delete page title.
        if self.__page_title is not None:
            self.__page_title.delete()
            self.__page_title = None

        if self.__current_prop_icon is not None:
            self.__current_prop_icon.delete()
            self.__current_prop_icon = None

        # Delete any pre-existent prop texts and icons.
        for prop_text in self.__prop_texts:
            prop_text.delete()
        # for prop_icon in self.__prop_icons:
        #     prop_icon.delete()

        self.__prop_texts = []

    def set_page(self, page: str) -> None:
        self.clear_page()

        self.__page_title = EditorMenuTitleNode(
            view_width = self.__view_width,
            view_height = self.__view_height,
            text = list(self.__prop_names.keys())[self.__current_page],
            batch = self.__batch
        )

        self.__prop_texts = [TextNode(
            x = self.__view_width / 2 + ((index - self.__current_prop) * 50),
            y = 10,
            width = self.__view_width,
            text = prop_name,
            color = (0xFF, 0xFF, 0xFF, 0xFF) if self.__current_prop == index else (0x00, 0x00, 0x00, 0xFF),
            font_name = "rughai",
            anchor_x = "center",
            align = "center",
            batch = self.__batch
        ) for index, prop_name in enumerate(self.__prop_names[page])]

        # self.__prop_icons = 

        current_page_name = list(self.__prop_names.keys())[self.__current_page]
        current_prop_name = list(self.__prop_names.values())[self.__current_page][self.__current_prop]
        icon = pyglet.resource.image(f"sprites/prop/{current_page_name}/{current_prop_name}/{current_prop_name}_icon.png")
        icon.anchor_x = icon.width / 2
        icon.anchor_y = icon.height / 2
        self.__current_prop_icon = SpriteNode(
            resource = icon,
            x = self.__view_width / 2,
            y = self.__view_height / 2,
            z = 100.0,
            batch = self.__batch
        )

class PropPlacementScene(Node):
    def __init__(
        self,
        window: pyglet.window.Window,
        view_width: int,
        view_height: int,
        source: str,
        on_ended: Optional[Callable[[dict], None]] = None
    ):
        super().__init__()
        self.__window = window
        self.__on_ended = on_ended

        # Define the scene.
        self.__scene = SceneNode(
            window = window,
            view_width = view_width,
            view_height = view_height,
            cam_speed = SETTINGS[Builtins.CAMERA_SPEED],
            title = source
        )

        self.__prop_names = self.__load_prop_names(f"{pyglet.resource.path[0]}/props.json")
        self.__in_menu = False

        # Define a tilemap.
        tilemaps = TilemapNode.from_tmx_file(
            source = f"tilemaps/{source}.tmx",
            batch = self.__scene.world_batch
        )
        self.__tile_size = tilemaps[0].get_tile_size()[0]
        tilemap_width = tilemaps[0].map_width
        tilemap_height = tilemaps[0].map_height
        cam_bounds = tilemaps[0].bounds

        # Cursor.
        cursor_position = (
            (tilemap_width / 2) * self.__tile_size,
            (tilemap_height / 2) * self.__tile_size
        )

        # TODO Replace with lines.
        cursor_image = pyglet.resource.image("sprites/extras/battery/battery_open.png")
        cursor_image.anchor_x = cursor_image.width / 2
        cursor_image.anchor_y = 0
        cursor_child = SpriteNode(
            resource = cursor_image,
            batch = self.__scene.world_batch
        )
        cursor_child = RectNode(
            x = cursor_position[0],
            y = cursor_position[1],
            width = self.__tile_size,
            height = self.__tile_size,
            anchor_x = self.__tile_size / 2,
            anchor_y = self.__tile_size / 2,
            color = (0xFF, 0xFF, 0x33, 0x7F),
            batch = self.__scene.world_batch
        )
        cam_target = PositionNode()
        self.__cursor = MapCursornode(
            tile_width = self.__tile_size,
            tile_height = self.__tile_size,
            child = cursor_child,
            cam_target = cam_target,
            x = cursor_position[0] + self.__tile_size / 2,
            y = cursor_position[1] + self.__tile_size / 2
        )

        self.__menu = PropEditorMenuNode(
            prop_names = self.__prop_names,
            view_width = view_width,
            view_height = view_height,
            open = self.__in_menu,
            batch = self.__scene.ui_batch,
            on_open = self.__on_menu_open,
            on_close = self.__on_menu_close
        )

        # Action sign.
        self.__action_sign = ActionSign(
            x = self.__tile_size,
            y = view_height - self.__tile_size,
            action = EditorAction.DELETE,
            batch = self.__scene.ui_batch
        )
        self.__action_sign.show()

        # Clouds.
        clouds = CloudsNode(
            bounds = cam_bounds,
            batch = self.__scene.world_batch
        )

        # Fetch current prop maps.
        self.__prop_maps = PropLoader.fetch_prop_maps(
            source = f"propmaps/{source}"
        )
        self.__props: List[PositionNode] = []
        self.__refresh_props()

        self.__scene.set_cam_bounds(cam_bounds)

        self.__scene.add_children(tilemaps)
        self.__scene.add_child(cam_target, cam_target = True)
        self.__scene.add_child(self.__action_sign)
        self.__scene.add_child(clouds)
        self.__scene.add_child(self.__cursor)
        self.__scene.add_child(self.__menu)

    def draw(self) -> None:
        if self.__scene is not None:
            self.__scene.draw()

    def update(self, dt) -> None:
        if not self.__menu.is_open():
            if controllers.INPUT_CONTROLLER.get_interaction():
                if self.__action_sign.action == EditorAction.INSERT:
                    # Add the currently selected prop if the interaction button was pressed.
                    if self.__menu.get_current_prop() not in list(self.__prop_maps.keys()):
                        self.__prop_maps[self.__menu.get_current_prop()] = set()
                    self.__prop_maps[self.__menu.get_current_prop()].add(self.__cursor.get_map_position())
                else:
                    # Delete anything in the current map position, regardless of the selected prop.
                    for prop_set in list(self.__prop_maps.values()):
                        prop_set.discard(self.__cursor.get_map_position())

                # Refresh props to apply changes.
                self.__refresh_props()

        if self.__scene is not None:
            self.__scene.update(dt)

    def delete(self) -> None:
        if self.__scene is not None:
            self.__scene.delete()

    def __refresh_props(self) -> None:
        # Delete all existing props.
        for prop in self.__props:
            if prop is not None:
                prop.delete()
        self.__props.clear()

        # Recreate all of them starting from prop maps.
        for prop_name in list(self.__prop_maps.keys()):
            for position in self.__prop_maps[prop_name]:
                self.__props.append(map_prop(
                    prop_name,
                    x = position[0] * self.__tile_size + self.__tile_size / 2,
                    y = position[1] * self.__tile_size,
                    batch = self.__scene.world_batch
                ))

    def __load_prop_names(self, source: str) -> Dict[str, List[str]]:
        data: Dict[str, List[str]]

        # Load JSON file.
        with open(file = source, mode = "r", encoding = "UTF-8") as content:
            data = json.load(content)

        return data

    def __on_menu_open(self) -> None:
        self.__cursor.disable_controls()
        self.__action_sign.hide()

    def __on_menu_close(self) -> None:
        self.__cursor.enable_controls()
        self.__action_sign.show()