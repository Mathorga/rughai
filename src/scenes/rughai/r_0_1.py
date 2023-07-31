from typing import Callable, Optional
import pyglet
from clouds_node import CloudsNode

from engine.door_node import DoorNode
from engine.node import PositionNode
from engine.playable_scene_node import PlayableSceneNode
from engine.prop_loader import PropLoader
from engine.scene_node import Bounds, SceneNode
from engine.sprite_node import SpriteNode
from engine.tilemap_node import TilemapNode
from engine.settings import SETTINGS, Builtins

from player_node import PlayerNode
import constants.events as events
import constants.scenes as scenes

class R_0_1(PlayableSceneNode):
    def __init__(
        self,
        window: pyglet.window.Window,
        view_width: int,
        view_height: int,
        scaling: int = 1,
        bundle: Optional[dict] = None,
        on_ended: Optional[Callable[[dict], None]] = None
    ):
        super().__init__(
            window = window,
            view_width = view_width,
            view_height = view_height,
            scaling = scaling,
            bundle = bundle,
            on_ended = on_ended
        )

        # Define the scene.
        self._scene = SceneNode(
            window = window,
            view_width = view_width,
            view_height = view_height,
            scaling = scaling,
            cam_speed = SETTINGS[Builtins.CAMERA_SPEED],
            title = "R_0_1",
            on_scene_end = self._on_scene_end
        )

        # Define a tilemap.
        tilemaps = TilemapNode.from_tmx_file(
            source = "tilemaps/rughai/r_0_1.tmx",
            scaling = scaling,
            batch = self._scene.world_batch
        )
        self.__tile_size = tilemaps[0].get_tile_size()[0]
        tilemap_width = tilemaps[0].map_width
        tilemap_height = tilemaps[0].map_height
        cam_bounds = Bounds(
            top = tilemap_height * self.__tile_size,
            bottom = 0,
            left = (-20) * self.__tile_size,
            right = tilemap_width * self.__tile_size
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
            scaling = scaling,
            batch = self._scene.world_batch
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
            scaling = scaling,
            batch = self._scene.world_batch
        )

        # Place doors.
        north_door = DoorNode(
            x = 18 * self.__tile_size,
            y = 30 * self.__tile_size,
            width = 32 * self.__tile_size,
            height = 2 * self.__tile_size,
            scaling = scaling,
            tags = ["player"],
            on_triggered = lambda entered:
                self.on_door_triggered(
                    entered = entered,
                    bundle = {
                        "event": events.CHANGE_ROOM,
                        "next_scene": scenes.R_0_0,
                        "player_position": [
                            self._player.x,
                            self.__tile_size
                        ]
                    }
                ),
            batch = self._scene.world_batch
        )
        south_west_door = DoorNode(
            x = 5 * self.__tile_size,
            y = -2 * self.__tile_size,
            width = 10 * self.__tile_size,
            height = 2 * self.__tile_size,
            scaling = scaling,
            tags = ["player"],
            on_triggered = lambda entered:
                self.on_door_triggered(
                    entered = entered,
                    bundle = {
                        "event": events.CHANGE_ROOM,
                        "next_scene": scenes.R_0_2,
                        "player_position": [
                            self._player.x,
                            49 * self.__tile_size
                        ]
                    }
                ),
            batch = self._scene.world_batch
        )
        south_east_door = DoorNode(
            x = 34 * self.__tile_size,
            y = -2 * self.__tile_size,
            width = 16 * self.__tile_size,
            height = 2 * self.__tile_size,
            scaling = scaling,
            tags = ["player"],
            on_triggered = lambda entered:
                self.on_door_triggered(
                    entered = entered,
                    bundle = {
                        "event": events.CHANGE_ROOM,
                        "next_scene": scenes.R_0_2,
                        "player_position": [
                            self._player.x,
                            49 * self.__tile_size
                        ]
                    }
                ),
            batch = self._scene.world_batch
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
            scaling = scaling,
            batch = self._scene.ui_batch
        )
        health_bar = SpriteNode(
            resource = bar_img,
            x = 4,
            y = view_height - 12,
            z = 500,
            scaling = scaling,
            batch = self._scene.ui_batch
        )

        # Clouds.
        clouds = CloudsNode(
            bounds = cam_bounds,
            scaling = scaling,
            batch = self._scene.world_batch
        )

        # Props.
        props = PropLoader.fetch_props(
            "propmaps/rughai/r_0_1",
            scaling = scaling,
            batch = self._scene.world_batch
        )

        self._scene.set_cam_bounds(cam_bounds)

        self._scene.add_child(bg)
        self._scene.add_children(tilemaps)
        self._scene.add_child(cam_target, cam_target = True)
        self._scene.add_child(clouds)
        self._scene.add_children(props)
        self._scene.add_child(self._player)
        self._scene.add_child(north_door)
        self._scene.add_child(south_west_door)
        self._scene.add_child(south_east_door)
        self._scene.add_child(energy_bar)
        self._scene.add_child(health_bar)