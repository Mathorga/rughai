from typing import Callable, List, Optional
import pyglet

from engine.door_node import DoorNode
from engine.node import PositionNode
from engine.playable_scene_node import PlayableSceneNode
from engine.prop_loader import PropLoader
from engine.scene_node import Bounds, SceneNode
from engine.sprite_node import SpriteNode
from engine.tilemap_node import TilemapNode
from engine.wall_node import WallNode
from engine.settings import SETTINGS, Builtins

from player_node import PlayerNode
from clouds_node import CloudsNode
import constants.events as events
import constants.scenes as scenes
from battery_node import BatteryNode
from stan_lee_node import StanLeeNode

class TestRoom(PlayableSceneNode):
    def __init__(
        self,
        window: pyglet.window.Window,
        view_width: int,
        view_height: int,
        bundle: Optional[dict] = None,
        on_ended: Optional[Callable[[dict], None]] = None
    ):
        super().__init__(
            window = window,
            view_width = view_width,
            view_height = view_height,
            bundle = bundle,
            on_ended = on_ended
        )

        # Define the scene.
        self._scene = SceneNode(
            window = window,
            view_width = view_width,
            view_height = view_height,
            cam_speed = SETTINGS[Builtins.CAMERA_SPEED],
            title = "R_0_0",
            on_scene_end = self._on_scene_end
        )

        # Define a tilemap.
        tilemaps = TilemapNode.from_tmx_file(
            source = "tilemaps/rughai/r_0_0.tmx",
            batch = self._scene.world_batch
        )
        self.__tile_size = tilemaps[0].get_tile_size()[0]
        tilemap_width = tilemaps[0].map_width
        tilemap_height = tilemaps[0].map_height
        cam_bounds = Bounds(
            bottom = SETTINGS[Builtins.TILEMAP_BUFFER] * self.__tile_size,
            right = (tilemap_width - 2 * SETTINGS[Builtins.TILEMAP_BUFFER]) * self.__tile_size,
            left = (-20) * self.__tile_size,
            top = (tilemap_height - 2 * SETTINGS[Builtins.TILEMAP_BUFFER]) * self.__tile_size
        )

        # Solid walls.
        walls: List[PositionNode] = [
            WallNode(
                x = self.__tile_size * 40,
                y = self.__tile_size * 25,
                width = self.__tile_size * 4,
                height = self.__tile_size * 2,
                batch = self._scene.world_batch
            )
        ]

        # Player.
        player_position = (
            bundle["player_position"][0] if bundle else 25 * self.__tile_size,
            bundle["player_position"][1] if bundle else 25 * self.__tile_size,
        )
        cam_target = PositionNode()
        self._player = PlayerNode(
            cam_target = cam_target,
            x = player_position[0],
            y = player_position[1],
            collision_tag = "player",
            batch = self._scene.world_batch
        )

        self._scene.set_cam_bounds(cam_bounds)

        self._scene.add_children(tilemaps)
        self._scene.add_children(walls)
        self._scene.add_child(cam_target, cam_target = True)
        self._scene.add_child(self._player)