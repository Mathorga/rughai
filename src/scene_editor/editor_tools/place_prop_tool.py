

import json
from typing import Callable, Dict, List, Optional, Tuple

import pyglet

from engine import controllers
from engine.node import Node, PositionNode
from engine.shapes.rect_node import RectNode
from engine.sprite_node import SpriteNode
from engine.text_node import TextNode
from scene_editor.editor_tools.editor_tool import EditorTool

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
            x = self.x,
            y = self.y,
            width = view_width / 2,
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
            x = self.x,
            y = self.y,
            width = view_width / 2,
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
        start_open: bool = False,
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
        self.__open = start_open

        # Current page.
        self.__current_page_index: int = 0
        self.__page_title: Optional[EditorMenuTitleNode] = None

        # Elements in the current page.
        self.__prop_texts: List[TextNode] = []

        # Currently selected element.
        self.__current_prop_index: int = 0
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
                self.__current_page_index -= 1
                self.__current_page_index = self.__current_page_index % len(self.__prop_names)
            if controllers.INPUT_CONTROLLER.get_menu_page_right():
                self.__current_page_index += 1
                self.__current_page_index = self.__current_page_index % len(self.__prop_names)

            # Prop selection.
            self.__current_prop_index -= controllers.INPUT_CONTROLLER.get_cursor_movement().y
            if self.__current_prop_index < 0:
                self.__current_prop_index = 0
            if self.__current_prop_index >= len(self.__prop_names[list(self.__prop_names.keys())[self.__current_page_index]]):
                self.__current_prop_index = len(self.__prop_names[list(self.__prop_names.keys())[self.__current_page_index]]) - 1

            self.set_page(list(self.__prop_names.keys())[self.__current_page_index])

    def get_current_page(self) -> str:
        return list(self.__prop_names.keys())[self.__current_page_index]

    def get_current_prop(self) -> str:
        return self.__prop_names[list(self.__prop_names.keys())[self.__current_page_index]][self.__current_prop_index]

    def get_current_image(self) -> pyglet.image.TextureRegion:
        current_page_name = self.get_current_page()
        current_prop_name = self.get_current_prop()
        icon = pyglet.resource.image(f"sprites/prop/{current_page_name}/{current_prop_name}/{current_prop_name}_icon.png")
        icon.anchor_x = icon.width / 2
        icon.anchor_y = icon.height / 2

        return icon

    def is_open(self) -> bool:
        return self.__open
    
    def toggle(self) -> None:
        if self.__open:
            self.close()
        else:
            self.open()

    def open(self) -> None:
        self.__open = True

        self.set_page(list(self.__prop_names.keys())[self.__current_page_index])

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

        self.__prop_texts = []

    def set_page(self, page: str) -> None:
        self.clear_page()

        self.__page_title = EditorMenuTitleNode(
            view_width = self.__view_width,
            view_height = self.__view_height,
            text = list(self.__prop_names.keys())[self.__current_page_index],
            batch = self.__batch
        )

        self.__prop_texts = [
            TextNode(
                # x = self.__view_width / 2 + ((index - self.__current_prop_index) * 50),
                # y = 10,
                x = 10,
                y = self.__view_height / 2 - ((index - self.__current_prop_index) * 10),
                width = self.__view_width,
                text = prop_name,
                color = (0xFF, 0xFF, 0xFF, 0xFF) if self.__current_prop_index == index else (0x00, 0x00, 0x00, 0xFF),
                font_name = "rughai",
                anchor_x = "left",
                align = "left",
                batch = self.__batch
            ) for index, prop_name in enumerate(self.__prop_names[page])
        ]

        if len(list(self.__prop_names.values())[self.__current_page_index]) > 0:
            icon = self.get_current_image()
            self.__current_prop_icon = SpriteNode(
                resource = icon,
                x = self.__view_width * 3 / 5,
                y = self.__view_height / 2,
                z = 100.0,
                batch = self.__batch
            )

class PlacePropTool(EditorTool):
    def __init__(
        self,
        view_width: int,
        view_height: int
    ) -> None:
        super().__init__()

        self.__prop_names = self.__load_prop_names(f"{pyglet.resource.path[0]}/props.json")
        self.__in_menu = False

        self.__menu = PropEditorMenuNode(
            prop_names = self.__prop_names,
            view_width = view_width,
            view_height = view_height,
            start_open = self.__in_menu,
            batch = self.__scene.ui_batch,
            on_open = self.__on_menu_open,
            on_close = self.__on_menu_close
        )

    def open_config(self) -> None:
        return super().open_config()

    def run(self, position: Tuple[int, int]) -> None:
        return super().run()

    def __load_prop_names(self, source: str) -> Dict[str, List[str]]:
        data: Dict[str, List[str]]

        # Load JSON file.
        with open(file = source, mode = "r", encoding = "UTF-8") as content:
            data = json.load(content)

        return data