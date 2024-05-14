from typing import Callable, list, Optional
import pyglet
from constants import collision_tags

from engine.door_node import DoorNode
from engine.node import PositionNode
from engine.playable_scene_node import PlayableSceneNode
from idle_prop_loader import IdlePropLoader
from engine.scene_node import Bounds, SceneNode
from engine.sprite_node import SpriteNode
from engine.tilemap_node import TilemapNode
from engine.wall_node import WallNode
from engine.settings import SETTINGS, Keys

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
        uniques.ACTIVE_SCENE = SceneNode(
            window = window,
            view_width = view_width,
            view_height = view_height,
            default_cam_speed = SETTINGS[Keys.CAMERA_SPEED],
            title = "R_0_0",
            on_scene_end = self._on_scene_end
        )

        # Define a tilemap.
        tilemaps = TilemapNode.from_tmx_file(
            source = "tilemaps/rughai/r_0_0.tmx",
            batch = uniques.ACTIVE_SCENE.world_batch
        )
        self.__tile_size = tilemaps[0].get_tile_size()[0]
        tilemap_width = tilemaps[0].map_width
        tilemap_height = tilemaps[0].map_height
        cam_bounds = Bounds(
            bottom = SETTINGS[Keys.TILEMAP_BUFFER] * self.__tile_size,
            right = (tilemap_width - 2 * SETTINGS[Keys.TILEMAP_BUFFER]) * self.__tile_size,
            left = (-20) * self.__tile_size,
            top = (tilemap_height - 2 * SETTINGS[Keys.TILEMAP_BUFFER]) * self.__tile_size
        )

        # Solid walls.
        walls: list[PositionNode] = [
            # Square.
            WallNode(
                x = self.__tile_size * 40,
                y = self.__tile_size * 25,
                width = self.__tile_size * 4,
                height = self.__tile_size * 1,
                tags = [collision_tags.PLAYER_COLLISION],
                batch = uniques.ACTIVE_SCENE.world_batch
            ),
            WallNode(
                x = self.__tile_size * 43,
                y = self.__tile_size * 25,
                width = self.__tile_size * 1,
                height = self.__tile_size * 4,
                tags = [collision_tags.PLAYER_COLLISION],
                batch = uniques.ACTIVE_SCENE.world_batch
            ),
            WallNode(
                x = self.__tile_size * 40,
                y = self.__tile_size * 28,
                width = self.__tile_size * 4,
                height = self.__tile_size * 1,
                tags = [collision_tags.PLAYER_COLLISION],
                batch = uniques.ACTIVE_SCENE.world_batch
            ),
            WallNode(
                x = self.__tile_size * 40,
                y = self.__tile_size * 25,
                width = self.__tile_size * 1,
                height = self.__tile_size * 4,
                tags = [collision_tags.PLAYER_COLLISION],
                batch = uniques.ACTIVE_SCENE.world_batch
            ),

            # Angle.
            WallNode(
                x = self.__tile_size * 40,
                y = self.__tile_size * 20,
                width = self.__tile_size * 4,
                height = self.__tile_size * 1,
                batch = uniques.ACTIVE_SCENE.world_batch
            ),
            WallNode(
                x = self.__tile_size * 40,
                y = self.__tile_size * 17,
                width = self.__tile_size * 1,
                height = self.__tile_size * 4,
                batch = uniques.ACTIVE_SCENE.world_batch
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
            batch = uniques.ACTIVE_SCENE.world_batch
        )

        uniques.ACTIVE_SCENE.set_cam_bounds(cam_bounds)

        uniques.ACTIVE_SCENE.add_children(tilemaps)
        uniques.ACTIVE_SCENE.add_children(walls)
        uniques.ACTIVE_SCENE.add_child(cam_target, cam_target = True)
        uniques.ACTIVE_SCENE.add_child(self._player)