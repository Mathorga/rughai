from typing import Callable, List, Optional
import pyglet

from engine.door_node import DoorNode
from engine.node import PositionNode
from engine.playable_scene_node import PlayableSceneNode
from prop_loader import PropLoader
from engine.scene_node import SceneNode
from engine.sprite_node import SpriteNode
from engine.tilemap_node import TilemapNode
from engine.wall_node import WallNode
from engine.settings import SETTINGS, Keys
from engine import controllers

from constants import collision_tags
from player_node import PlayerNode
from clouds_node import CloudsNode
import constants.events as events
import constants.scenes as scenes
from battery_node import BatteryNode
from stan_lee_node import StanLeeNode
from walls_loader import WallsLoader

class R_0_0(PlayableSceneNode):
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
        scenes.ACTIVE_SCENE = SceneNode(
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
        tilemaps: List[TilemapNode] = TilemapNode.from_tmx_file(
            source = "tilemaps/r_0_0.tmx",
            batch = scenes.ACTIVE_SCENE.world_batch
        )
        self.__tile_size = tilemaps[0].get_tile_size()[0]
        tilemap_width = tilemaps[0].map_width
        tilemap_height = tilemaps[0].map_height
        cam_bounds = tilemaps[0].bounds

        # Solid walls.
        walls: List[WallNode] = WallsLoader.fetch(
            source = "wallmaps/r_0_0.json",
            batch = scenes.ACTIVE_SCENE.world_batch
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
            z = -500,
            batch = scenes.ACTIVE_SCENE.world_batch
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
            batch = scenes.ACTIVE_SCENE.world_batch
        )

        # Place doors.
        south_door = DoorNode(
            x = 40 * self.__tile_size,
            y = 0,
            width = 32 * self.__tile_size,
            height = 2 * self.__tile_size,
            tags = [collision_tags.PLAYER_SENSE],
            on_triggered = lambda tags, entered:
                self.on_door_triggered(
                    entered = entered,
                    bundle = {
                        "event": events.CHANGE_ROOM,
                        "next_scene": scenes.R_0_1,
                        "player_position": [
                            self._player.x,
                            30 * self.__tile_size
                        ]
                    }
                ),
            batch = scenes.ACTIVE_SCENE.world_batch
        )
        east_door = DoorNode(
            x = (tilemap_width - 2) * self.__tile_size,
            y = 27 * self.__tile_size,
            width = 2 * self.__tile_size,
            height = 19 * self.__tile_size,
            tags = [collision_tags.PLAYER_SENSE],
            on_triggered = lambda tags, entered:
                self.on_door_triggered(
                    entered = entered,
                    bundle = {
                        "event": events.CHANGE_ROOM,
                        "next_scene": scenes.R_0_6,
                        "player_position": [
                            self.__tile_size,
                            self._player.y
                        ]
                    }
                ),
            batch = scenes.ACTIVE_SCENE.world_batch
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
            batch = scenes.ACTIVE_SCENE.ui_batch
        )
        health_bar = SpriteNode(
            resource = bar_img,
            x = 4,
            y = view_height - 12,
            z = 500,
            batch = scenes.ACTIVE_SCENE.ui_batch
        )

        # Clouds.
        clouds = CloudsNode(
            bounds = cam_bounds,
            batch = scenes.ACTIVE_SCENE.world_batch
        )

        # Props.
        props = PropLoader.fetch_prop_list(
            "propmaps/r_0_0",
            batch = scenes.ACTIVE_SCENE.world_batch
        )

        # Stan Lee.
        stan_lee = StanLeeNode(
            x = self.__tile_size * 48,
            y = self.__tile_size * 35,
            world_batch = scenes.ACTIVE_SCENE.world_batch,
            ui_batch = scenes.ACTIVE_SCENE.ui_batch
        )
        self.battery = BatteryNode(
            x = self.__tile_size * 58,
            y = self.__tile_size * 35,
            on_interaction = self.delete_battery,
            batch = scenes.ACTIVE_SCENE.world_batch
        )

        scenes.ACTIVE_SCENE.set_cam_bounds(cam_bounds)

        scenes.ACTIVE_SCENE.add_child(bg)
        scenes.ACTIVE_SCENE.add_children(tilemaps)
        scenes.ACTIVE_SCENE.add_children(walls)
        scenes.ACTIVE_SCENE.add_child(cam_target, cam_target = True)
        scenes.ACTIVE_SCENE.add_child(clouds)
        scenes.ACTIVE_SCENE.add_children(props)
        scenes.ACTIVE_SCENE.add_child(stan_lee)
        scenes.ACTIVE_SCENE.add_child(self.battery)
        scenes.ACTIVE_SCENE.add_child(self._player)
        scenes.ACTIVE_SCENE.add_child(south_door)
        scenes.ACTIVE_SCENE.add_child(east_door)
        scenes.ACTIVE_SCENE.add_child(energy_bar)
        scenes.ACTIVE_SCENE.add_child(health_bar)

    def delete_battery(self) -> None:
        if scenes.ACTIVE_SCENE is not None:
            scenes.ACTIVE_SCENE.remove_child(self.battery)
        self.battery.delete()