from enum import Enum
from typing import Callable, Optional
import pyglet

from engine.prop_loader import PropLoader
from engine.node import Node, PositionNode
from engine.scene_node import SceneNode
from engine.sprite_node import SpriteNode
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
        self._window = window
        self._on_ended = on_ended

        # Define the scene.
        self._scene = SceneNode(
            window = window,
            view_width = view_width,
            view_height = view_height,
            cam_speed = SETTINGS[Builtins.CAMERA_SPEED],
            title = source
        )

        # Define a tilemap.
        tilemaps = TilemapNode.from_tmx_file(
            source = f"tilemaps/{source}.tmx",
            batch = self._scene.world_batch
        )
        self.__tile_size = tilemaps[0].get_tile_size()[0]
        tilemap_width = tilemaps[0].map_width
        tilemap_height = tilemaps[0].map_height
        cam_bounds = tilemaps[0].bounds

        # Player.
        player_position = (
            (tilemap_width / 2) * self.__tile_size,
            (tilemap_height / 2) * self.__tile_size
        )
        cam_target = PositionNode()
        self.__cursor = EditorCursornode(
            tile_size = self.__tile_size,
            cam_target = cam_target,
            x = player_position[0],
            y = player_position[1],
            batch = self._scene.world_batch
        )

        # Action sign.
        action_sign = ActionSign(
            x = self.__tile_size,
            y = view_height - self.__tile_size,
            action = EditorAction.DELETE,
            batch = self._scene.ui_batch
        )

        # Clouds.
        clouds = CloudsNode(
            bounds = cam_bounds,
            batch = self._scene.world_batch
        )

        # Props.
        props = PropLoader.fetch_props(
            source = f"propmaps/{source}",
            batch = self._scene.world_batch
        )

        self._scene.set_cam_bounds(cam_bounds)

        self._scene.add_children(tilemaps)
        self._scene.add_child(cam_target, cam_target = True)
        self._scene.add_child(action_sign)
        self._scene.add_child(clouds)
        self._scene.add_children(props)
        self._scene.add_child(self.__cursor)

    def draw(self) -> None:
        if self._scene is not None:
            self._scene.draw()

    def update(self, dt) -> None:
        if self._scene is not None:
            self._scene.update(dt)

    def delete(self) -> None:
        if self._scene is not None:
            self._scene.delete()