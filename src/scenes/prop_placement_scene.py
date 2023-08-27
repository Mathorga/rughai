from enum import Enum
import json
import os
from typing import Callable, Dict, List, Optional, Text
import pyglet
from engine import controllers

from engine.prop_loader import PropLoader
from engine.node import Node, PositionNode
from engine.scene_node import SceneNode
from engine.shapes.rect_node import RectNode
from engine.sprite_node import SpriteNode
from engine.text_node import TextNode
from engine.tilemap_node import TilemapNode
from engine.settings import SETTINGS, Builtins

from clouds_node import CloudsNode
from editor_cursor_node import EditorCursornode

class EditorAction(str, Enum):
    # Settings.
    ADD = "add_editor_action"
    EDIT = "edit_editor_action"
    DELETE = "delete_editor_action"

class ActionSign(PositionNode):
    def __init__(
        self,
        x: float = 0.0,
        y: float = 0.0,
        action: EditorAction = EditorAction.ADD,
        batch: Optional[pyglet.graphics.Batch] = None
    ) -> None:
        super().__init__(
            x = x,
            y = y
        )

        self.action = action
        
        image = pyglet.resource.image(f"sprites/{action.value}.png")
        image.anchor_x = 0
        image.anchor_y = image.height
        self.__sprite = SpriteNode(
            resource = image,
            x = x,
            y = y,
            z = 500,
            batch = batch
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
            text = "< (Q/L)",
            align = "left",
            anchor_x = "center",
            font_name = "rughai",
            batch = batch
        )
        self.__text = TextNode(
            x = self.x,
            y = self.y,
            text = text,
            align = "center",
            anchor_x = "center",
            font_name = "rughai",
            batch = batch
        )
        self.__right_arrow = TextNode(
            x = self.x - 10,
            y = self.y,
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
            color = (0x83, 0x94, 0xC8),
            batch = self.__batch
        )
        self.__background.set_opacity(0xAF)

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

        # Delete any pre-existent prop icons.
        for prop_text in self.__prop_texts:
            prop_text.delete()

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
            text = prop_name,
            font_name = "rughai",
            anchor_x = "center",
            align = "center",
            batch = self.__batch
        ) for index, prop_name in enumerate(self.__prop_names[page])]

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

        self.__props_map = self.__load_props_map(f"{pyglet.resource.path[0]}/props.json")
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
        cam_target = PositionNode()
        self.__cursor = EditorCursornode(
            tile_size = self.__tile_size,
            cam_target = cam_target,
            x = cursor_position[0],
            y = cursor_position[1],
            batch = self.__scene.world_batch
        )

        self.__menu = PropEditorMenuNode(
            prop_names = self.__props_map,
            view_width = view_width,
            view_height = view_height,
            open = self.__in_menu,
            batch = self.__scene.ui_batch,
            on_open = lambda: self.__cursor.disable_controls(),
            on_close = lambda: self.__cursor.enable_controls()
        )

        # Action sign.
        action_sign = ActionSign(
            x = self.__tile_size,
            y = view_height - self.__tile_size,
            action = EditorAction.DELETE,
            batch = self.__scene.ui_batch
        )

        # Clouds.
        clouds = CloudsNode(
            bounds = cam_bounds,
            batch = self.__scene.world_batch
        )

        # Props.
        props = PropLoader.fetch_props(
            source = f"propmaps/{source}",
            batch = self.__scene.world_batch
        )

        self.__scene.set_cam_bounds(cam_bounds)

        self.__scene.add_children(tilemaps)
        self.__scene.add_child(cam_target, cam_target = True)
        self.__scene.add_child(action_sign)
        self.__scene.add_child(clouds)
        self.__scene.add_children(props)
        self.__scene.add_child(self.__cursor)
        self.__scene.add_child(self.__menu)

    def draw(self) -> None:
        if self.__scene is not None:
            self.__scene.draw()

    def update(self, dt) -> None:
        if self.__scene is not None:
            self.__scene.update(dt)

    def delete(self) -> None:
        if self.__scene is not None:
            self.__scene.delete()

    def __load_props_map(self, source: str) -> Dict[str, List[str]]:
        data: Dict[str, List[str]]

        # Load JSON file.
        with open(file = source, mode = "r", encoding = "UTF-8") as content:
            data = json.load(content)

        return data