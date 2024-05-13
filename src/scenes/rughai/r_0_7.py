from typing import Callable, Optional
import pyglet

from clouds_node import CloudsNode
from constants import uniques
from doors_loader import DoorsLoader
from engine.door_node import DoorNode
from engine.fall_node import FallNode
from engine.node import PositionNode
from engine.playable_scene_node import PlayableSceneNode
from engine.wall_node import WallNode
from falls_loader import FallsLoader
from idle_prop_loader import IdlePropLoader
from engine.scene_node import SceneNode
from engine.sprite_node import SpriteNode
from engine.tilemap_node import TilemapNode
from engine.settings import SETTINGS, Keys

from player_node import PlayerNode
import constants.scenes as scenes
from walls_loader import WallsLoader

class R_0_7(PlayableSceneNode):
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
            title = "R_0_7",
            on_scene_end = self._on_scene_end,
            on_scene_start = self._on_scene_start
        )

        # Define a tilemap.
        tilemaps: list[TilemapNode] = TilemapNode.from_tmx_file(
            source = "tilemaps/r_0_7.tmx",
            batch = uniques.ACTIVE_SCENE.world_batch
        )
        self.__tile_size = tilemaps[0].get_tile_size()[0]
        tilemap_width = tilemaps[0].map_width
        tilemap_height = tilemaps[0].map_height
        cam_bounds = tilemaps[0].bounds

        # Solid walls.
        walls: list[WallNode] = WallsLoader.fetch(
            source = "wallmaps/r_0_7.json",
            batch = uniques.ACTIVE_SCENE.world_batch
        )

        # Falls.
        falls: list[FallNode] = FallsLoader.fetch(
            source = "fallmaps/r_0_7.json",
            batch = uniques.ACTIVE_SCENE.world_batch
        )

        # Define a background.
        bg_image = pyglet.resource.image("bg.png")
        bg_image.anchor_x = bg_image.width / 2
        bg_image.anchor_y = bg_image.height / 2
        bg = SpriteNode(
            resource = bg_image,
            on_animation_end = lambda : None,
            x = (tilemaps[0].map_width * self.__tile_size) // 2,
            y = (tilemaps[0].map_height * self.__tile_size) // 2,
            z = -500,
            batch = uniques.ACTIVE_SCENE.world_batch
        )

        # Player.
        player_position = (
            bundle["player_position"][0] if bundle else 10 * self.__tile_size,
            bundle["player_position"][1] if bundle else 10 * self.__tile_size,
        )
        cam_target = PositionNode()
        self._player = PlayerNode(
            cam_target = cam_target,
            x = player_position[0],
            y = player_position[1],
            batch = uniques.ACTIVE_SCENE.world_batch
        )

        # Place doors.
        doors: list[DoorNode] = DoorsLoader.fetch(
            source = "doormaps/r_0_7.json",
            tile_size = (self.__tile_size, self.__tile_size),
            on_triggered = self.on_door_triggered,
            batch = uniques.ACTIVE_SCENE.world_batch
        )

        # Define energy bars.
        bar_img = pyglet.resource.image("sprites/energy_bar.png")
        bar_img.anchor_x = 0
        bar_img.anchor_y = bar_img.height
        energy_bar = SpriteNode(
            resource = bar_img,
            x = 4,
            y = view_height - 4,
            z = 500,
            batch = uniques.ACTIVE_SCENE.ui_batch
        )
        health_bar = SpriteNode(
            resource = bar_img,
            x = 4,
            y = view_height - 12,
            z = 500,
            batch = uniques.ACTIVE_SCENE.ui_batch
        )

        # Clouds.
        clouds = CloudsNode(
            bounds = cam_bounds,
            batch = uniques.ACTIVE_SCENE.world_batch
        )

        # Props.
        props = IdlePropLoader.fetch(
            source = "propmaps/r_0_7.json",
            batch = uniques.ACTIVE_SCENE.world_batch
        )

        uniques.ACTIVE_SCENE.set_cam_bounds(cam_bounds)

        uniques.ACTIVE_SCENE.add_child(bg)
        uniques.ACTIVE_SCENE.add_children(tilemaps)
        uniques.ACTIVE_SCENE.add_children(walls)
        uniques.ACTIVE_SCENE.add_children(falls)
        uniques.ACTIVE_SCENE.add_child(cam_target, cam_target = True)
        uniques.ACTIVE_SCENE.add_child(clouds)
        uniques.ACTIVE_SCENE.add_children(props)
        uniques.ACTIVE_SCENE.add_child(self._player)
        uniques.ACTIVE_SCENE.add_children(doors)
        uniques.ACTIVE_SCENE.add_child(energy_bar)
        uniques.ACTIVE_SCENE.add_child(health_bar)