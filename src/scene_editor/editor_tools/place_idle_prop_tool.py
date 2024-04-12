import copy
import sys
import os
import json
from typing import Callable, Dict, List, Optional, Set, Tuple
import pyglet

sys.path.append(os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".")))

from engine import controllers
from engine.node import Node, PositionNode
from idle_prop_loader import IdlePropLoader
from engine.shapes.rect_node import RectNode
from engine.sprite_node import SpriteNode
from engine.text_node import TextNode
from editor_tool import EditorTool

TOOL_COLOR: Tuple[int, int, int, int] = (0x22, 0x44, 0x66, 0xAA)
ALT_COLOR: Tuple[int, int, int, int] = (0xFF, 0x00, 0x00, 0x7F)

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

class IdlePropEditorMenuNode(Node):
    def __init__(
        self,
        prop_names: Dict[str, List[str]],
        view_width: int,
        view_height: int,
        start_open: bool = False,
        batch: Optional[pyglet.graphics.Batch] = None,
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

        self.__background: Optional[RectNode] = None

    def update(self, dt: int) -> None:
        super().update(dt)

        if self.__open:
            # Only handle controls if open:
            # Page change.
            if controllers.INPUT_CONTROLLER.get_menu_page_left():
                self.__current_page_index -= 1
                self.__current_page_index = self.__current_page_index % len(self.__prop_names)
            if controllers.INPUT_CONTROLLER.get_menu_page_right():
                self.__current_page_index += 1
                self.__current_page_index = self.__current_page_index % len(self.__prop_names)

            # Prop selection.
            self.__current_prop_index -= int(controllers.INPUT_CONTROLLER.get_cursor_movement().y)
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

    def open(self) -> None:
        self.__open = True

        self.set_page(list(self.__prop_names.keys())[self.__current_page_index])

        self.__background = RectNode(
            x = 0.0,
            y = 0.0,
            z = -100.0,
            width = self.__view_width,
            height = self.__view_height,
            color = (0x33, 0x33, 0x33, 0xDD),
            batch = self.__batch
        )

    def close(self) -> None:
        self.__open = False

        self.clear_page()

        if self.__background is not None:
            self.__background.delete()
            self.__background = None

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

class PlaceIdlePropTool(EditorTool):
    def __init__(
        self,
        view_width: int,
        view_height: int,
        tile_size: Tuple[int, int],
        tilemap_width: int,
        tilemap_height: int,
        scene_name: str,
        on_icon_changed: Optional[Callable] = None,
        world_batch: Optional[pyglet.graphics.Batch] = None,
        ui_batch: Optional[pyglet.graphics.Batch] = None
    ) -> None:
        super().__init__(
            on_icon_changed = on_icon_changed
        )

        self.__prop_names: Dict[str, List[str]] = self.__load_prop_names(f"{pyglet.resource.path[0]}/props.json")
        self.__in_menu: bool = False
        self.__scene_name: str = scene_name
        self.__world_batch: Optional[pyglet.graphics.Batch] = world_batch
        self.__ui_batch: Optional[pyglet.graphics.Batch] = ui_batch

        self.__tile_size: Tuple[int, int] = tile_size
        self.__tilemap_width: int = tilemap_width
        self.__tilemap_height: int = tilemap_height

        self.__prop_sets: List[Dict[str, Set[Tuple[int, int]]]] = [
            IdlePropLoader.fetch_prop_sets(
                source = f"propmaps/{scene_name}"
            )
        ]
        self.__current_props_index: int = 0

        self.__props: List[PositionNode] = []
        self.__refresh_props()

        self.__menu: IdlePropEditorMenuNode = IdlePropEditorMenuNode(
            prop_names = self.__prop_names,
            view_width = view_width,
            view_height = view_height,
            start_open = self.__in_menu,
            batch = self.__ui_batch,
        )

        self.name = "Place idle prop"
        self.color = TOOL_COLOR

    def get_cursor_icon(self) -> PositionNode:
        # Return a tile-sized rectangle if in alternate mode, the currently selected prop otherwise.
        return RectNode(
            x = 0.0,
            y = 0.0,
            width = self.__tile_size[0],
            height = self.__tile_size[1],
            anchor_x = self.__tile_size[0] / 2,
            anchor_y = self.__tile_size[1] / 2,
            color = ALT_COLOR,
            batch = self.__world_batch
        ) if self.alt_mode else IdlePropLoader.map_prop(
            self.__menu.get_current_prop(),
            x = 0.0,
            y = 0.0,
            batch = self.__world_batch
        )

    def update(self, dt: int) -> None:
        super().update(dt)

        self.__menu.update(dt = dt)

    def toggle_menu(self, toggle: bool) -> None:
        super().toggle_menu(toggle)
        if toggle:
            self.__menu.open()
        else:
            self.__menu.close()

    def toggle_alt_mode(self, toggle: bool) -> None:
        super().toggle_alt_mode(toggle)

        # Notify icon changed.
        if self.on_icon_changed is not None:
            self.on_icon_changed()

    def run(self, map_position: Tuple[int, int]) -> None:
        super().run(map_position = map_position)

        if self.alt_mode:
            # Just clear if in alt mode.
            self.clear(position = map_position)
        else:
            # Place the currently selected prop otherwise.
            self.place_prop(position = map_position)

        IdlePropLoader.save_prop_sets(
            dest = f"{pyglet.resource.path[0]}/propmaps/{self.__scene_name}",
            map_width = self.__tilemap_width,
            map_height = self.__tilemap_height,
            prop_sets = self.__prop_sets[self.__current_props_index]
        )

    def place_prop(self, position: Tuple[int, int]) -> None:
        # Clear history until the current index is reached.
        self.__prop_sets = self.__prop_sets[0:self.__current_props_index + 1]

        # Add an entry in the prop sets history.
        self.__prop_sets.append(copy.deepcopy(self.__prop_sets[self.__current_props_index]))

        prop_sets_size = len(self.__prop_sets)
        if prop_sets_size > 20:
            self.__prop_sets = self.__prop_sets[prop_sets_size - 20:prop_sets_size]
        else:
            self.__current_props_index += 1

        # Add the currently selected prop if the interaction button was pressed.
        if self.__menu.get_current_prop() not in list(self.__prop_sets[self.__current_props_index].keys()):
            self.__prop_sets[self.__current_props_index][self.__menu.get_current_prop()] = set()
        self.__prop_sets[self.__current_props_index][self.__menu.get_current_prop()].add(position)

        # Refresh props to apply changes.
        self.__refresh_props()

    def clear(self, position: Tuple[int, int]) -> None:
        """
        Deletes any prop in the current map position, regardless of the selected prop.
        """

        # Loop through prop types and delete any in the given position.
        for prop_set in list(self.__prop_sets[self.__current_props_index].values()):
            prop_set.discard(position)

        # Refresh props to apply changes.
        self.__refresh_props()

    def undo(self) -> None:
        super().undo()

        self.__current_props_index -= 1
        if self.__current_props_index < 0:
            self.__current_props_index = 0
        self.__refresh_props()

    def redo(self) -> None:
        super().redo()
        self.__current_props_index += 1
        if self.__current_props_index > len(self.__prop_sets) - 1:
            self.__current_props_index = len(self.__prop_sets) - 1
        self.__refresh_props()

    def __load_prop_names(self, source: str) -> Dict[str, List[str]]:
        data: Dict[str, List[str]]

        # Load JSON file.
        with open(file = source, mode = "r", encoding = "UTF-8") as content:
            data = json.load(content)

        return data

    def __refresh_props(self) -> None:
        # Delete all existing props.
        for prop in self.__props:
            if prop is not None:
                prop.delete()
        self.__props.clear()

        # Recreate all of them starting from prop maps.
        for prop_name in list(self.__prop_sets[self.__current_props_index].keys()):
            for position in self.__prop_sets[self.__current_props_index][prop_name]:
                prop = IdlePropLoader.map_prop(
                    prop_name,
                    x = position[0] * self.__tile_size[0] + self.__tile_size[0] / 2,
                    y = position[1] * self.__tile_size[1] + self.__tile_size[1] / 2,
                    batch = self.__world_batch
                )

                if prop is not None:
                    self.__props.append(prop)