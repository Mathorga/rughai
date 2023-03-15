from typing import Callable, Optional
import pyglet
from engine.collision_manager import CollisionManager

from engine.node import PositionNode
from engine.scene_manager_node import SceneManagerNode
from engine.scene_node import Bounds, SceneNode
from engine.sensor_node import SensorNode
from engine.sprite_node import SpriteNode
from engine.input_controller import InputController
from engine.tilemap_node import TilemapNode

from player_node import PlayerNode
from duk_node import DukNode
import constants.events as events
import constants.scenes as scenes

class RugHaiHub(SceneManagerNode):
    def __init__(
        self,
        window: pyglet.window.Window,
        collision_manager: CollisionManager,
        input_controller: InputController,
        view_width: int,
        view_height: int,
        scaling: int = 1,
        bundle: Optional[dict] = None,
        on_ended: Optional[Callable[[dict], None]] = None
    ):
        super().__init__(
            window = window,
            collision_manager = collision_manager,
            input_controller = input_controller,
            view_width = view_width,
            view_height = view_height,
            scaling = scaling,
            bundle = bundle,
            on_ended = on_ended
        )

        # Define a tilemap.
        tilemaps = TilemapNode.from_tmx_file(
            source = "tilemaps/rughai/main_hub.tmx",
            scaling = scaling
        )
        self.__tile_size = tilemaps[0].get_tile_size()[0]

        # Define a background.
        bg_image = pyglet.resource.image("bg.png")
        bg_image.anchor_x = bg_image.width / 2
        bg_image.anchor_y = bg_image.height / 2
        bg = SpriteNode(
            resource = pyglet.resource.image("bg.png"),
            on_animation_end = lambda : None,
            x = (tilemaps[0].map_width * self.__tile_size) // 2,
            y = (tilemaps[0].map_height * self.__tile_size) // 2,
            scaling = scaling
        )

        # Player.
        cam_target = PositionNode()
        self.__player = PlayerNode(
            input_controller = input_controller,
            collision_manager = collision_manager,
            cam_target = cam_target,
            x = 10 * self.__tile_size,
            y = 10 * self.__tile_size,
            scaling = scaling,
            collision_tag = "player"
        )

        # Duk.
        duk = DukNode(
            x = 10 * self.__tile_size,
            y = 8 * self.__tile_size,
            scaling = scaling
        )

        # Define tree prop.
        # TODO Use dedicated class.
        tree_img = pyglet.resource.image("sprites/rughai/prop/tree_l.png")
        tree_img.anchor_x = tree_img.width / 2
        tree_img.anchor_y = 3
        tree = SpriteNode(
            resource = tree_img,
            x = 5 * self.__tile_size,
            y = 5 * self.__tile_size,
            scaling = scaling
        )

        # Place doors.
        bottom_door = SensorNode(
            x = 25 * self.__tile_size,
            y = 0,
            width = 50 * self.__tile_size,
            height = 2 * self.__tile_size,
            anchor_x = 25 * self.__tile_size,
            anchor_y = 2 * self.__tile_size,
            scaling = scaling,
            visible = True,
            tag = "player",
            on_triggered = self.on_bottom_door_triggered
        )
        collision_manager.add_collider(bottom_door)

        # Define energy bars.
        bar_img = pyglet.resource.image("sprites/energy_bar.png")
        bar_img.anchor_x = 0
        bar_img.anchor_y = bar_img.height
        energy_bar = SpriteNode(
            resource = bar_img,
            x = 4,
            y = view_height - 4,
            scaling = scaling
        )
        health_bar = SpriteNode(
            resource = bar_img,
            x = 4,
            y = view_height - 12,
            scaling = scaling
        )

        self._scene = SceneNode(
            window = window,
            view_width = view_width,
            view_height = view_height,
            scaling = scaling,
            cam_speed = 5.0,
            cam_bounds = Bounds(
                top = 50 * self.__tile_size,
                bottom = 0,
                right = 50 * self.__tile_size,
                scaling = scaling
            ),
            on_scene_end = self.__on_scene_end
        )

        self._scene.add_child(bg)
        self._scene.add_children(tilemaps)
        self._scene.add_child(cam_target, cam_target = True)
        self._scene.add_child(self.__player, sorted = True)
        self._scene.add_child(duk, sorted = True)
        self._scene.add_child(tree, sorted = True)
        self._scene.add_child(bottom_door)
        self._scene.add_child(energy_bar, ui = True)
        self._scene.add_child(health_bar, ui = True)

    def on_bottom_door_triggered(self, value: bool):
        if value:
            if self._scene is not None:
                self._scene.end()
            self.__player.disable_controls()

    def __on_scene_end(self) -> None:
        if self._on_ended:
            # Pass a package containing all useful information for the next room.
            self._on_ended(
                {
                    "event": events.CHANGE_ROOM,
                    "next_scene": scenes.RUGHAI_BOTTOM,
                    "player_position": [
                        self.__player.x,
                        25 * self.__tile_size
                    ]
                }
            )