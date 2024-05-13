from typing import Callable
import pyglet

from constants import uniques
from doors_loader import DoorsLoader
from engine.door_node import DoorNode
from engine.fall_node import FallNode
from engine.node import PositionNode
from engine.playable_scene_node import PlayableSceneNode
from falls_loader import FallsLoader
from idle_prop_loader import IdlePropLoader
from engine.scene_node import SceneNode
from engine.sprite_node import SpriteNode
from engine.tilemap_node import TilemapNode
from engine.wall_node import WallNode
from engine.settings import SETTINGS, Keys
from engine import controllers
from engine.utils import utils

from player_node import PlayerNode
from clouds_node import CloudsNode
from prop_loader import PropLoader
from walls_loader import WallsLoader

class R_0_0(PlayableSceneNode):
    def __init__(
        self,
        window: pyglet.window.Window,
        view_width: int,
        view_height: int,
        bundle: dict | None = None,
        on_ended: Callable[[dict], None] | None = None
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
            on_scene_start = self._on_scene_start,
            on_scene_end = self._on_scene_end
        )

        # Scene music.
        self.scene_music: pyglet.media.Source = pyglet.resource.media(name = "sounds/rughai_myst.wav")
        controllers.SOUND_CONTROLLER.set_music(self.scene_music)

        # Define a tilemap.
        tilemaps: list[TilemapNode] = TilemapNode.from_tmx_file(
            source = "tilemaps/r_0_0.tmx",
            batch = uniques.ACTIVE_SCENE.world_batch
        )
        self.__tile_size = tilemaps[0].get_tile_size()[0]
        tilemap_width = tilemaps[0].map_width
        tilemap_height = tilemaps[0].map_height
        cam_bounds = tilemaps[0].bounds

        # Solid walls.
        walls: list[WallNode] = WallsLoader.fetch(
            source = "wallmaps/r_0_0.json",
            batch = uniques.ACTIVE_SCENE.world_batch
        )

        # Falls.
        falls: list[FallNode] = FallsLoader.fetch(
            source = "fallmaps/r_0_0.json",
            batch = uniques.ACTIVE_SCENE.world_batch
        )

        # Define a background.
        bg_image = pyglet.resource.image("bg.png")
        bg_image.anchor_x = bg_image.width / 2
        bg_image.anchor_y = bg_image.height / 2
        bg = SpriteNode(
            resource = bg_image,
            on_animation_end = lambda : None,
            x = (tilemap_width * self.__tile_size) // 2,
            y = (tilemap_height * self.__tile_size) // 2,
            z = -1500,
            batch = uniques.ACTIVE_SCENE.world_batch
        )

        # Player.
        player_position = (
            bundle["player_position"][0] if bundle else 50 * self.__tile_size,
            bundle["player_position"][1] if bundle else 25 * self.__tile_size,
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
            source = "doormaps/r_0_0.json",
            tile_size = (self.__tile_size, self.__tile_size),
            on_triggered = self.on_door_triggered,
            batch = uniques.ACTIVE_SCENE.world_batch
        )

        # Define energy bars.
        bar_img = pyglet.resource.image("sprites/energy_bar.png")
        utils.set_anchor(resource = bar_img, x = 0.0, y = bar_img.height)
        energy_bar = SpriteNode(
            resource = bar_img,
            x = 4,
            y = view_height - 4,
            z = 500.0,
            batch = uniques.ACTIVE_SCENE.ui_batch
        )
        health_bar = SpriteNode(
            resource = bar_img,
            x = 4,
            y = view_height - 12,
            z = 500.0,
            batch = uniques.ACTIVE_SCENE.ui_batch
        )
        quik_img: pyglet.image.TextureRegion = pyglet.resource.image("sprites/menus/hud/quik.png")
        utils.set_anchor(
            resource = quik_img,
            x = quik_img.width / 2,
            y = 0.0
        )
        quik: SpriteNode = SpriteNode(
            resource = quik_img,
            x = view_width / 2,
            y = 0.0,
            z = 500.0,
            batch = uniques.ACTIVE_SCENE.ui_batch
        )

        # Clouds.
        clouds = CloudsNode(
            bounds = cam_bounds,
            batch = uniques.ACTIVE_SCENE.world_batch
        )

        # Props.
        idle_props = IdlePropLoader.fetch(
            source = "idlepropmaps/r_0_0.json",
            batch = uniques.ACTIVE_SCENE.world_batch
        )
        props = PropLoader.fetch(
            source = "propmaps/r_0_0.json",
            world_batch = uniques.ACTIVE_SCENE.world_batch,
            ui_batch = uniques.ACTIVE_SCENE.ui_batch
        )

        uniques.ACTIVE_SCENE.set_cam_bounds(cam_bounds)

        uniques.ACTIVE_SCENE.add_child(bg)
        uniques.ACTIVE_SCENE.add_children(tilemaps)
        uniques.ACTIVE_SCENE.add_children(walls)
        uniques.ACTIVE_SCENE.add_children(falls)
        uniques.ACTIVE_SCENE.add_child(cam_target, cam_target = True)
        uniques.ACTIVE_SCENE.add_child(clouds)
        uniques.ACTIVE_SCENE.add_children(idle_props)
        uniques.ACTIVE_SCENE.add_children(props)
        uniques.ACTIVE_SCENE.add_child(self._player)
        uniques.ACTIVE_SCENE.add_children(doors)
        uniques.ACTIVE_SCENE.add_child(energy_bar)
        uniques.ACTIVE_SCENE.add_child(health_bar)
        uniques.ACTIVE_SCENE.add_child(quik)