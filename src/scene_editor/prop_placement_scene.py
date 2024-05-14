from typing import Callable
import pyglet

from constants import scenes
from engine import controllers
from engine.node import Node, PositionNode
from engine.scene_node import Bounds, SceneNode
from engine.shapes.line_node import LineNode
from engine.text_node import TextNode
from engine.tilemap_node import TilemapNode
from engine.settings import SETTINGS, Keys
from engine.map_cursor_node import MapCursorNode

from editor_tools.editor_tool import EditorTool, PlaceDoorTool
from editor_tools.place_idle_prop_tool import PlaceIdlePropTool
from editor_tools.place_wall_tool import PlaceWallTool
from editor_tools.place_prop_tool import PlacePropTool
from editor_tools.place_fall_tool import PlaceFallTool

class ActionSign(PositionNode):
    def __init__(
        self,
        view_width: float,
        view_height: float,
        x: float = 0.0,
        y: float = 0.0,
        tool_name: str = "",
        room_name: str = "",
        color: tuple[int, int, int, int] = (0x00, 0x00, 0x00, 0xFF),
        batch: pyglet.graphics.Batch | None = None
    ) -> None:
        super().__init__(
            x = x,
            y = y
        )

        self.__view_width = view_width
        self.__view_height = view_height

        self.__batch = batch
        self.__tool_label: TextNode | None = None
        self.__room_label: TextNode | None = None

        self.tool_name = tool_name
        self.room_name = room_name
        self.color = color
        self.visible = True

    def set_tool_text(self, text: str) -> None:
        self.tool_name = text

        if self.__tool_label is not None:
            self.__tool_label.set_text(text = self.__get_tool_text())

    def set_room_text(self, text: str) -> None:
        self.room_name = text

        if self.__room_label is not None:
            self.__room_label.set_text(text = self.__get_room_text())

    def set_color(self, color: tuple[int, int, int, int]) -> None:
        self.color = color

        if self.__tool_label is not None:
            self.__tool_label.set_color(color = color)

    def __get_tool_text(self) -> str:
        return f"(tab) {self.tool_name}"

    def __get_room_text(self) -> str:
        return f"(<Q) {self.room_name} (E>)"

    def hide(self) -> None:
        self.visible = False

        if self.__tool_label is not None:
            self.__tool_label.delete()
            self.__tool_label = None

        if self.__room_label is not None:
            self.__room_label.delete()
            self.__room_label = None

    def show(self) -> None:
        self.visible = True

        if self.__tool_label is None:
            self.__tool_label = TextNode(
                x = self.x,
                y = self.y,
                width = 0.0,
                anchor_x = "left",
                text = self.__get_tool_text(),
                color = self.color,
                font_name = "rughai",
                multiline = False,
                batch = self.__batch
            )

        if self.__room_label is None:
            self.__room_label = TextNode(
                x = self.__view_width - self.x,
                y = self.y,
                width = 0-0,
                anchor_x = "right",
                text = self.__get_room_text(),
                color = self.color,
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
        on_ended: Callable[[dict], None] | None = None
    ):
        super().__init__()
        self.__window = window
        self.__on_ended = on_ended
        self.__view_width = view_width
        self.__view_height = view_height

        self.__tile_size: tuple[int, int]
        self.__tilemap_width: int
        self.__tilemap_height: int
        cam_bounds: Bounds

        # Define all rooms.
        self.__rooms: list[str] = [
            "r_0_0",
            "r_0_1",
            "r_0_2",
            "r_0_3",
            "r_0_4",
            "r_0_5",
            "r_0_6",
            "r_0_7",
            "r_0_8"
        ]
        self.__current_room: int = 0

        # All tools are in this dictionary.
        self.__tools: list[EditorTool]

        # Editor tool.
        self.__current_tool: int = 0

        # Defines whether the current tool's menu is open or not.
        self.__menu_open: bool = False

        # Define a map cursor.
        self.__cursor: MapCursorNode

        # Action sign.
        self.__action_sign: ActionSign

        self.__bound_lines: list[LineNode]

        self.__setup(self.__rooms[self.__current_room])

    def draw(self) -> None:
        if uniques.ACTIVE_SCENE is not None:
            uniques.ACTIVE_SCENE.draw()

    def update(self, dt) -> None:
        self.__tools[self.__current_tool].update(dt = dt)

        # Toggle open/close upon start key pressed.
        if controllers.INPUT_CONTROLLER.get_start():
            self.__toggle_menu()

        # Toggle current tool's alt mode.
        self.__tools[self.__current_tool].toggle_alt_mode(controllers.INPUT_CONTROLLER.get_tool_alt())

        if not self.__menu_open:
            # Switch tool.
            if controllers.INPUT_CONTROLLER.get_switch():
                self.__current_tool += 1
                self.__current_tool %= len(self.__tools)

                self.__update_cursor_icon()
                self.__action_sign.set_tool_text(self.__tools[self.__current_tool].name)
                self.__action_sign.set_room_text(self.__rooms[self.__current_room])
                self.__action_sign.set_color(self.__tools[self.__current_tool].color)

            # Change scene.
            if controllers.INPUT_CONTROLLER.get_menu_page_left():
                self.__current_room -= 1
                self.__current_room %= len(self.__rooms)
                self.__setup(self.__rooms[self.__current_room])
            elif controllers.INPUT_CONTROLLER.get_menu_page_right():
                self.__current_room += 1
                self.__current_room %= len(self.__rooms)
                self.__setup(self.__rooms[self.__current_room])

            # Run the current tool.
            if controllers.INPUT_CONTROLLER.get_tool_run():
                self.__tools[self.__current_tool].run(self.__cursor.get_map_position())

            # Undo/redo the last tool's action.
            if controllers.INPUT_CONTROLLER.get_redo():
                self.__tools[self.__current_tool].redo()
            elif controllers.INPUT_CONTROLLER.get_undo():
                self.__tools[self.__current_tool].undo()

        if uniques.ACTIVE_SCENE is not None:
            uniques.ACTIVE_SCENE.update(dt)

    def delete(self) -> None:
        if uniques.ACTIVE_SCENE is not None:
            uniques.ACTIVE_SCENE.delete()

    def __setup(self, scene_name: str) -> None:
        # Delete the current scene and recreate everything.
        self.delete()

        # Define the scene.
        uniques.ACTIVE_SCENE = SceneNode(
            window = self.__window,
            view_width = self.__view_width,
            view_height = self.__view_height,
            default_cam_speed = SETTINGS[Keys.CAMERA_SPEED],
            title = scene_name
        )

        # Define a tilemap.
        tilemaps: list[TilemapNode] = TilemapNode.from_tmx_file(
            source = f"tilemaps/{scene_name}.tmx",
            batch = uniques.ACTIVE_SCENE.world_batch
        )
        self.__tile_size: tuple[int, int] = tilemaps[0].get_tile_size()
        self.__tilemap_width = tilemaps[0].map_width
        self.__tilemap_height = tilemaps[0].map_height
        cam_bounds = tilemaps[0].bounds

        # Cursor.
        cursor_position = (
            (self.__tilemap_width / 2) * self.__tile_size[0],
            (self.__tilemap_height / 2) * self.__tile_size[1]
        )

        # All tools are in this dictionary.
        self.__tools: list[EditorTool] = [
            PlaceIdlePropTool(
                view_width = self.__view_width,
                view_height = self.__view_height,
                tilemap_width = self.__tilemap_width,
                tilemap_height = self.__tilemap_height,
                tile_size = self.__tile_size,
                scene_name = scene_name,
                on_icon_changed = self.__update_cursor_icon,
                world_batch = uniques.ACTIVE_SCENE.world_batch,
                ui_batch = uniques.ACTIVE_SCENE.ui_batch
            ),
            PlacePropTool(
                view_width = self.__view_width,
                view_height = self.__view_height,
                tilemap_width = self.__tilemap_width,
                tilemap_height = self.__tilemap_height,
                tile_size = self.__tile_size,
                scene_name = scene_name,
                on_icon_changed = self.__update_cursor_icon,
                world_batch = uniques.ACTIVE_SCENE.world_batch,
                ui_batch = uniques.ACTIVE_SCENE.ui_batch
            ),
            PlaceWallTool(
                view_width = self.__view_width,
                view_height = self.__view_height,
                tile_size = self.__tile_size,
                scene_name = scene_name,
                on_icon_changed = self.__update_cursor_icon,
                world_batch = uniques.ACTIVE_SCENE.world_batch,
                ui_batch = uniques.ACTIVE_SCENE.ui_batch
            ),
            PlaceFallTool(
                view_width = self.__view_width,
                view_height = self.__view_height,
                tile_size = self.__tile_size,
                scene_name = scene_name,
                on_icon_changed = self.__update_cursor_icon,
                world_batch = uniques.ACTIVE_SCENE.world_batch,
                ui_batch = uniques.ACTIVE_SCENE.ui_batch
            ),
            PlaceDoorTool(
                tile_size = self.__tile_size,
                batch = uniques.ACTIVE_SCENE.world_batch
            )
        ]

        # Editor tool.
        self.__current_tool: int = 0

        # Defines whether the current tool's menu is open or not.
        self.__menu_open: bool = False

        # Define a map cursor.
        cam_target: PositionNode = PositionNode()
        self.__cursor: MapCursorNode = MapCursorNode(
            tile_width = self.__tile_size[0],
            tile_height = self.__tile_size[1],
            child = self.__tools[self.__current_tool].get_cursor_icon(),
            cam_target = cam_target,
            on_move = self.__on_cursor_move,
            x = cursor_position[0] + self.__tile_size[0] / 2,
            y = cursor_position[1] + self.__tile_size[1] / 2
        )

        # Action sign.
        self.__action_sign: ActionSign = ActionSign(
            x = self.__tile_size[0],
            y = self.__view_height - self.__tile_size[1],
            view_width = self.__view_width,
            view_height = self.__view_height,
            tool_name = self.__tools[self.__current_tool].name,
            room_name = self.__rooms[self.__current_room],
            color = self.__tools[self.__current_tool].color,
            batch = uniques.ACTIVE_SCENE.ui_batch
        )
        self.__action_sign.show()

        self.__bound_lines = [
            LineNode(
                x = 0.0,
                y = 0.0,
                delta_x = (self.__tilemap_width) * self.__tile_size[0],
                delta_y = 0.0,
                color = (0xFF, 0x33, 0x00, 0x7F),
                batch = uniques.ACTIVE_SCENE.world_batch
            ),
            LineNode(
                x = self.__tilemap_width * self.__tile_size[0],
                y = 0.0,
                delta_x = 0.0,
                delta_y = self.__tilemap_height * self.__tile_size[1],
                color = (0xFF, 0x33, 0x00, 0x7F),
                batch = uniques.ACTIVE_SCENE.world_batch
            ),
            LineNode(
                x = 0.0,
                y = self.__tilemap_height * self.__tile_size[1],
                delta_x = self.__tilemap_width * self.__tile_size[0],
                delta_y = 0.0,
                color = (0xFF, 0x33, 0x00, 0x7F),
                batch = uniques.ACTIVE_SCENE.world_batch
            ),
            LineNode(
                x = 0.0,
                y = 0.0,
                delta_x = 0.0,
                delta_y = self.__tilemap_height * self.__tile_size[1],
                color = (0xFF, 0x33, 0x00, 0x7F),
                batch = uniques.ACTIVE_SCENE.world_batch
            )
        ]

        uniques.ACTIVE_SCENE.add_children(tilemaps)
        uniques.ACTIVE_SCENE.add_child(cam_target, cam_target = True)
        uniques.ACTIVE_SCENE.add_child(self.__action_sign)
        uniques.ACTIVE_SCENE.add_child(self.__cursor)

    def __on_cursor_move(self, position: tuple[int, int]) -> None:
        self.__tools[self.__current_tool].move_cursor(map_position = position)

    def __update_cursor_icon(self) -> None:
        self.__cursor.set_child(self.__tools[self.__current_tool].get_cursor_icon())

    def __toggle_menu(self) -> None:
        self.__menu_open = not self.__menu_open

        if self.__menu_open:
            self.__cursor.disable_controls()
            self.__action_sign.hide()
        else:
            self.__cursor.enable_controls()
            self.__action_sign.show()

        # Toggle the current tool.
        self.__tools[self.__current_tool].toggle_menu(self.__menu_open)