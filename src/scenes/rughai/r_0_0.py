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
from priest_node import PriestNode

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
            # House.
            WallNode(
                x = self.__tile_size * 43,
                y = self.__tile_size * 32,
                width = self.__tile_size,
                height = self.__tile_size * 6,
                batch = self._scene.world_batch
            ),
            WallNode(
                x = self.__tile_size * 44,
                y = self.__tile_size * 32,
                width = self.__tile_size,
                height = self.__tile_size,
                batch = self._scene.world_batch
            ),
            WallNode(
                x = self.__tile_size * 43,
                y = self.__tile_size * 38,
                width = self.__tile_size * 5,
                height = self.__tile_size,
                batch = self._scene.world_batch
            ),
            WallNode(
                x = self.__tile_size * 48,
                y = self.__tile_size * 38,
                width = self.__tile_size,
                height = self.__tile_size * 3,
                batch = self._scene.world_batch
            ),
            WallNode(
                x = self.__tile_size * 49,
                y = self.__tile_size * 40,
                width = self.__tile_size * 4,
                height = self.__tile_size,
                batch = self._scene.world_batch
            ),
            WallNode(
                x = self.__tile_size * 53,
                y = self.__tile_size * 34,
                width = self.__tile_size,
                height = self.__tile_size * 7,
                batch = self._scene.world_batch
            ),
            WallNode(
                x = self.__tile_size * 49,
                y = self.__tile_size * 34,
                width = self.__tile_size * 4,
                height = self.__tile_size,
                batch = self._scene.world_batch
            ),
            WallNode(
                x = self.__tile_size * 49,
                y = self.__tile_size * 32,
                width = self.__tile_size,
                height = self.__tile_size * 2,
                batch = self._scene.world_batch
            ),
            WallNode(
                x = self.__tile_size * 47,
                y = self.__tile_size * 32,
                width = self.__tile_size * 2,
                height = self.__tile_size,
                batch = self._scene.world_batch
            ),

            # Slopes.
            WallNode(
                x = self.__tile_size * 62,
                y = self.__tile_size * 29,
                width = self.__tile_size,
                height = self.__tile_size * 17,
                batch = self._scene.world_batch
            ),
            WallNode(
                x = self.__tile_size * 63,
                y = self.__tile_size * 29,
                width = self.__tile_size * 4,
                height = self.__tile_size * 2,
                batch = self._scene.world_batch
            ),
            WallNode(
                x = self.__tile_size * 66,
                y = self.__tile_size * 27,
                width = self.__tile_size,
                height = self.__tile_size * 2,
                batch = self._scene.world_batch
            ),
            WallNode(
                x = self.__tile_size * 66,
                y = self.__tile_size * 25,
                width = self.__tile_size * 4,
                height = self.__tile_size * 2,
                batch = self._scene.world_batch
            )
        ]

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
            batch = self._scene.world_batch
        )

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

        # Place doors.
        south_door = DoorNode(
            x = 19 * self.__tile_size,
            y = -2 * self.__tile_size,
            width = 31 * self.__tile_size,
            height = 2 * self.__tile_size,
            tags = ["player"],
            on_triggered = lambda entered:
                self.on_door_triggered(
                    entered = entered,
                    bundle = {
                        "event": events.CHANGE_ROOM,
                        "next_scene": scenes.R_0_1,
                        "player_position": [
                            self._player.x,
                            25 * self.__tile_size
                        ]
                    }
                ),
            batch = self._scene.world_batch
        )
        east_door = DoorNode(
            x = tilemap_width * self.__tile_size,
            y = 25 * self.__tile_size,
            width = 2 * self.__tile_size,
            height = 19 * self.__tile_size,
            tags = ["player"],
            on_triggered = lambda entered:
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
            batch = self._scene.ui_batch
        )
        health_bar = SpriteNode(
            resource = bar_img,
            x = 4,
            y = view_height - 12,
            z = 500,
            batch = self._scene.ui_batch
        )

        # Clouds.
        clouds = CloudsNode(
            bounds = cam_bounds,
            batch = self._scene.world_batch
        )

        # Props.
        props = PropLoader.fetch_props(
            "propmaps/rughai/r_0_0",
            batch = self._scene.world_batch
        )

        # Priest.
        priest = PriestNode(
            x = self.__tile_size * 46,
            y = self.__tile_size * 35,
            world_batch = self._scene.world_batch,
            ui_batch = self._scene.ui_batch
        )
        self.battery = BatteryNode(
            x = self.__tile_size * 58,
            y = self.__tile_size * 35,
            on_interaction = self.delete_battery,
            batch = self._scene.world_batch
        )

        self._scene.set_cam_bounds(cam_bounds)

        self._scene.add_child(bg)
        self._scene.add_children(tilemaps)
        self._scene.add_children(walls)
        self._scene.add_child(cam_target, cam_target = True)
        self._scene.add_child(clouds)
        self._scene.add_children(props)
        self._scene.add_child(priest)
        self._scene.add_child(self.battery)
        self._scene.add_child(self._player)
        self._scene.add_child(south_door)
        self._scene.add_child(east_door)
        self._scene.add_child(energy_bar)
        self._scene.add_child(health_bar)

    def delete_battery(self) -> None:
        if self._scene is not None:
            self._scene.remove_child(self.battery)
        self.battery.delete()