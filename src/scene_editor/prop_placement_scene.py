from typing import Callable, List, Optional, Tuple
import pyglet

from constants import scenes
from engine import controllers
from engine.node import Node, PositionNode
from engine.scene_node import SceneNode
from engine.shapes.line_node import LineNode
from engine.shapes.rect_node import RectNode
from engine.text_node import TextNode
from engine.tilemap_node import TilemapNode
from engine.settings import SETTINGS, Keys
from engine.map_cursor_node import MapCursorNode

from editor_tools.editor_tool import ChangeSceneTool, EditorTool, PlaceDoorTool
from editor_tools.place_prop_tool import PlacePropTool
from editor_tools.place_wall_tool import PlaceWallTool

class ActionSign(PositionNode):
    def __init__(
        self,
        x: float = 0.0,
        y: float = 0.0,
        action: str = "",
        color: Tuple[int, int, int, int] = (0x00, 0x00, 0x00, 0xFF),
        batch: Optional[pyglet.graphics.Batch] = None
    ) -> None:
        super().__init__(
            x = x,
            y = y
        )

        self.__batch = batch
        self.__label: Optional[TextNode] = None

        self.action = action
        self.color = color
        self.visible = True

    def set_text(self, text: str) -> None:
        self.action = text
        self.__label.set_text(text = self.__compute_text())

    def set_color(self, color: Tuple[int, int, int, int]) -> None:
        self.color = color
        self.__label.set_color(color = self.__compute_color())

    def __compute_text(self) -> str:
        return f"(tab) {self.action}"

    def __compute_color(self) -> Tuple[int, int, int, int]:
        return self.color

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
        scenes.ACTIVE_SCENE = SceneNode(
            window = window,
            view_width = view_width,
            view_height = view_height,
            default_cam_speed = SETTINGS[Keys.CAMERA_SPEED],
            title = scene_name
        )

        # Define a tilemap.
        tilemaps: List[TilemapNode] = TilemapNode.from_tmx_file(
            source = f"tilemaps/{scene_name}.tmx",
            batch = scenes.ACTIVE_SCENE.world_batch
        )
        self.__tile_size: Tuple[int, int] = tilemaps[0].get_tile_size()
        self.__tilemap_width = tilemaps[0].map_width
        self.__tilemap_height = tilemaps[0].map_height
        cam_bounds = tilemaps[0].bounds

        # Cursor.
        cursor_position = (
            (self.__tilemap_width / 2) * self.__tile_size[0],
            (self.__tilemap_height / 2) * self.__tile_size[1]
        )

        # All tools are in this dictionary.
        self.__tools: List[EditorTool] = [
            PlacePropTool(
                view_width = view_width,
                view_height = view_height,
                tilemap_width = self.__tilemap_width,
                tilemap_height = self.__tilemap_height,
                tile_size = self.__tile_size,
                scene_name = scene_name,
                on_icon_changed = self.__update_cursor_icon,
                world_batch = scenes.ACTIVE_SCENE.world_batch,
                ui_batch = scenes.ACTIVE_SCENE.ui_batch
            ),
            PlaceWallTool(
                view_width = view_width,
                view_height = view_height,
                tile_size = self.__tile_size,
                scene_name = scene_name,
                on_icon_changed = self.__update_cursor_icon,
                world_batch = scenes.ACTIVE_SCENE.world_batch,
                ui_batch = scenes.ACTIVE_SCENE.ui_batch
            ),
            PlaceDoorTool(
                tile_size = self.__tile_size,
                batch = scenes.ACTIVE_SCENE.world_batch
            ),
            ChangeSceneTool(
                tile_size = self.__tile_size,
                batch = scenes.ACTIVE_SCENE.world_batch
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
            y = view_height - self.__tile_size[1],
            action = self.__tools[self.__current_tool].name,
            color = self.__tools[self.__current_tool].color,
            batch = scenes.ACTIVE_SCENE.ui_batch
        )
        self.__action_sign.show()

        self.__bound_lines = [
            LineNode(
                x = 0.0,
                y = 0.0,
                delta_x = (self.__tilemap_width) * self.__tile_size[0],
                delta_y = 0.0,
                color = (0xFF, 0x33, 0x00, 0x7F),
                batch = scenes.ACTIVE_SCENE.world_batch
            ),
            LineNode(
                x = self.__tilemap_width * self.__tile_size[0],
                y = 0.0,
                delta_x = 0.0,
                delta_y = self.__tilemap_height * self.__tile_size[1],
                color = (0xFF, 0x33, 0x00, 0x7F),
                batch = scenes.ACTIVE_SCENE.world_batch
            ),
            LineNode(
                x = 0.0,
                y = self.__tilemap_height * self.__tile_size[1],
                delta_x = self.__tilemap_width * self.__tile_size[0],
                delta_y = 0.0,
                color = (0xFF, 0x33, 0x00, 0x7F),
                batch = scenes.ACTIVE_SCENE.world_batch
            ),
            LineNode(
                x = 0.0,
                y = 0.0,
                delta_x = 0.0,
                delta_y = self.__tilemap_height * self.__tile_size[1],
                color = (0xFF, 0x33, 0x00, 0x7F),
                batch = scenes.ACTIVE_SCENE.world_batch
            )
        ]

        scenes.ACTIVE_SCENE.add_children(tilemaps)
        scenes.ACTIVE_SCENE.add_child(cam_target, cam_target = True)
        scenes.ACTIVE_SCENE.add_child(self.__action_sign)
        scenes.ACTIVE_SCENE.add_child(self.__cursor)

    def draw(self) -> None:
        if scenes.ACTIVE_SCENE is not None:
            scenes.ACTIVE_SCENE.draw()

    def update(self, dt) -> None:
        self.__tools[self.__current_tool].update(dt = dt)

        # Toggle open/close upon start key pressed.
        if controllers.INPUT_CONTROLLER.get_start():
            self.__toggle_menu()

        # Toggle current tool's alt mode.
        self.__tools[self.__current_tool].toggle_alt_mode(controllers.INPUT_CONTROLLER.get_tool_alt())

        if not self.__menu_open:
            if controllers.INPUT_CONTROLLER.get_switch():
                # Switch action.
                self.__current_tool += 1
                self.__current_tool %= len(self.__tools)

                self.__update_cursor_icon()
                self.__action_sign.set_text(self.__tools[self.__current_tool].name)
                self.__action_sign.set_color(self.__tools[self.__current_tool].color)

            if controllers.INPUT_CONTROLLER.get_tool_run():
                self.__tools[self.__current_tool].run(self.__cursor.get_map_position())

            if controllers.INPUT_CONTROLLER.get_redo():
                self.__tools[self.__current_tool].redo()
            elif controllers.INPUT_CONTROLLER.get_undo():
                self.__tools[self.__current_tool].undo()

        if scenes.ACTIVE_SCENE is not None:
            scenes.ACTIVE_SCENE.update(dt)

    def delete(self) -> None:
        if scenes.ACTIVE_SCENE is not None:
            scenes.ACTIVE_SCENE.delete()

    def __on_cursor_move(self, position: Tuple[int, int]) -> None:
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