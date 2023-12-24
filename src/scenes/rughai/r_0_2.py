from typing import Callable, Optional
from constants import collision_tags
import pyglet
from clouds_node import CloudsNode
from engine.door_node import DoorNode

from engine.node import PositionNode
from engine.playable_scene_node import PlayableSceneNode
from engine.prop_loader import PropLoader
from engine.scene_node import SceneNode
from engine.sprite_node import SpriteNode
from engine.tilemap_node import TilemapNode
from engine.settings import SETTINGS, Keys

from player_node import PlayerNode
from duk_node import DukNode
import constants.events as events
import constants.scenes as scenes

class R_0_2(PlayableSceneNode):
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
            title = "R_0_2",
            on_scene_end = self._on_scene_end
        )

        # Define a tilemap.
        tilemaps = TilemapNode.from_tmx_file(
            source = "tilemaps/r_0_2.tmx",
            batch = scenes.ACTIVE_SCENE.world_batch
        )
        self.__tile_size = tilemaps[0].get_tile_size()[0]
        tilemap_width = tilemaps[0].map_width
        tilemap_height = tilemaps[0].map_height
        cam_bounds = tilemaps[0].bounds

        # Define a background.
        bg_image = pyglet.resource.image("bg.png")
        bg_image.anchor_x = bg_image.width / 2
        bg_image.anchor_y = bg_image.height / 2
        bg = SpriteNode(
            resource = pyglet.resource.image("bg.png"),
            on_animation_end = lambda : None,
            x = (tilemaps[0].map_width * self.__tile_size) // 2,
            y = (tilemaps[0].map_height * self.__tile_size) // 2,
            z = -500,
            batch = scenes.ACTIVE_SCENE.world_batch
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
            batch = scenes.ACTIVE_SCENE.world_batch
        )

        # Duk.
        # duk = DukNode(
        #     x = 10 * self.__tile_size,
        #     y = 8 * self.__tile_size,
        #     batch = self._scene.world_batch
        # )

        # Place doors.
        north_west_door = DoorNode(
            x = 5 * self.__tile_size,
            y = 50 * self.__tile_size,
            width = 10 * self.__tile_size,
            height = 2 * self.__tile_size,
            anchor_x = 0,
            anchor_y = 0,
            tags = [collision_tags.PLAYER_SENSE],
            on_triggered = lambda tags, entered:
                self.on_door_triggered(
                    entered = entered,
                    bundle = {
                        "event": events.CHANGE_ROOM,
                        "next_scene": scenes.R_0_1,
                        "player_position": [
                            self._player.x,
                            self.__tile_size
                        ]
                    }
                ),
            batch = scenes.ACTIVE_SCENE.world_batch
        )
        north_east_door = DoorNode(
            x = 32 * self.__tile_size,
            y = 50 * self.__tile_size,
            width = 18 * self.__tile_size,
            height = 2 * self.__tile_size,
            anchor_x = 0,
            anchor_y = 0,
            tags = [collision_tags.PLAYER_SENSE],
            on_triggered = lambda tags, entered:
                self.on_door_triggered(
                    entered = entered,
                    bundle = {
                        "event": events.CHANGE_ROOM,
                        "next_scene": scenes.R_0_1,
                        "player_position": [
                            self._player.x,
                            self.__tile_size
                        ]
                    }
                ),
            batch = scenes.ACTIVE_SCENE.world_batch
        )
        south_door = DoorNode(
            x = 19 * self.__tile_size,
            y = -2 * self.__tile_size,
            width = 31 * self.__tile_size,
            height = 2 * self.__tile_size,
            anchor_x = 0,
            anchor_y = 0,
            tags = [collision_tags.PLAYER_SENSE],
            on_triggered = lambda tags, entered:
                self.on_door_triggered(
                    entered = entered,
                    bundle = {
                        "event": events.CHANGE_ROOM,
                        "next_scene": scenes.R_0_3,
                        "player_position": [
                            self._player.x,
                            25 * self.__tile_size
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
            "propmaps/r_0_2",
            batch = scenes.ACTIVE_SCENE.world_batch
        )

        scenes.ACTIVE_SCENE.set_cam_bounds(cam_bounds)

        scenes.ACTIVE_SCENE.add_child(bg)
        scenes.ACTIVE_SCENE.add_children(tilemaps)
        scenes.ACTIVE_SCENE.add_child(cam_target, cam_target = True)
        scenes.ACTIVE_SCENE.add_child(self._player)
        # self._scene.add_child(duk)
        scenes.ACTIVE_SCENE.add_child(clouds)
        scenes.ACTIVE_SCENE.add_children(props)
        scenes.ACTIVE_SCENE.add_child(north_west_door)
        scenes.ACTIVE_SCENE.add_child(north_east_door)
        scenes.ACTIVE_SCENE.add_child(south_door)
        scenes.ACTIVE_SCENE.add_child(energy_bar)
        scenes.ACTIVE_SCENE.add_child(health_bar)