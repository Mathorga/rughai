from typing import Callable
import pyglet

import engine.controllers as controllers
from engine.door_node import DoorNode
from engine.fall_node import FallNode
from engine.node import Node, PositionNode
from engine.scene_node import SceneNode
from engine.settings import SETTINGS, Keys
from engine.sprite_node import SpriteNode
from engine.tilemap_node import TilemapNode
from engine.wall_node import WallNode
from engine.utils import utils

from doors_loader import DoorsLoader
from falls_loader import FallsLoader
from idle_prop_loader import IdlePropLoader
from inventory.inventory_node import InventoryNode, MenuNode
from player_node import PlayerNode
from prop_loader import PropLoader
from walls_loader import WallsLoader
from clouds_node import CloudsNode
from constants import uniques

class PlayableSceneNode(Node):
    """
    Node defining any playable (by a player) scene.

    Parameters
    ----------
    name: str
        Name of the scene.
    window: pyglet.window.Window
        Window.
    view_width: int
        Width of the in-game view.
    view_height: int
        Height of the in-game view.
    bundle: dict | None
        Starting bundle of the scene. The bundle is structured as follows:
        "destination"
    """

    def __init__(
        self,
        name: str,
        window: pyglet.window.Window,
        view_width: int,
        view_height: int,
        bundle: dict | None = None,
        on_ended: Callable[[dict], None] | None = None
    ) -> None:
        super().__init__()

        self.window = window
        self.on_ended = on_ended

        self.bundle: dict | None = bundle

        # Define the scene.
        uniques.ACTIVE_SCENE = SceneNode(
            window = window,
            view_width = view_width,
            view_height = view_height,
            default_cam_speed = SETTINGS[Keys.CAMERA_SPEED],
            title = name,
            on_scene_start = self._on_scene_start,
            on_scene_end = self._on_scene_end
        )

        # Inventory.
        inventory: InventoryNode = InventoryNode(
            view_width = view_width,
            view_height = view_height,
            world_batch = uniques.ACTIVE_SCENE.world_batch,
            ui_batch = uniques.ACTIVE_SCENE.ui_batch
        )
        menu: MenuNode = MenuNode(
            view_width = view_width,
            view_height = view_height,
            world_batch = uniques.ACTIVE_SCENE.world_batch,
            ui_batch = uniques.ACTIVE_SCENE.ui_batch
        )

        # Scene music.
        self.scene_music: pyglet.media.Source = pyglet.resource.media(name = "sounds/rughai_myst.wav")
        controllers.SOUND_CONTROLLER.set_music(self.scene_music)

        # Define a tilemap.
        tilemaps: list[TilemapNode] = TilemapNode.from_tmx_file(
            source = f"tilemaps/{name}.tmx",
            batch = uniques.ACTIVE_SCENE.world_batch
        )
        self.__tile_size = tilemaps[0].get_tile_size()[0]
        tilemap_width = tilemaps[0].map_width
        tilemap_height = tilemaps[0].map_height
        cam_bounds = tilemaps[0].bounds

        # Solid walls.
        walls: list[WallNode] = WallsLoader.fetch(
            source = f"wallmaps/{name}.json",
            batch = uniques.ACTIVE_SCENE.world_batch
        )

        # Falls.
        falls: list[FallNode] = FallsLoader.fetch(
            source = f"fallmaps/{name}.json",
            batch = uniques.ACTIVE_SCENE.world_batch
        )

        # Place doors.
        doors: list[DoorNode] = DoorsLoader.fetch(
            source = f"doormaps/{name}.json",
            tile_size = (self.__tile_size, self.__tile_size),
            on_triggered = self.on_door_triggered,
            batch = uniques.ACTIVE_SCENE.world_batch
        )

        # Props.
        idle_props = IdlePropLoader.fetch(
            source = f"idlepropmaps/{name}.json",
            batch = uniques.ACTIVE_SCENE.world_batch
        )
        props = PropLoader.fetch(
            source = f"propmaps/{name}.json",
            world_batch = uniques.ACTIVE_SCENE.world_batch,
            ui_batch = uniques.ACTIVE_SCENE.ui_batch
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
        self._player: PlayerNode = PlayerNode(
            cam_target = cam_target,
            x = player_position[0],
            y = player_position[1],
            batch = uniques.ACTIVE_SCENE.world_batch
        )

        # Clouds.
        clouds = CloudsNode(
            bounds = cam_bounds,
            batch = uniques.ACTIVE_SCENE.world_batch
        )

        uniques.ACTIVE_SCENE.set_cam_bounds(cam_bounds)

        uniques.ACTIVE_SCENE.add_child(bg)
        uniques.ACTIVE_SCENE.add_child(inventory)
        # uniques.ACTIVE_SCENE.add_child(menu)
        uniques.ACTIVE_SCENE.add_children(tilemaps)
        uniques.ACTIVE_SCENE.add_children(walls)
        uniques.ACTIVE_SCENE.add_children(falls)
        uniques.ACTIVE_SCENE.add_child(cam_target, cam_target = True)
        uniques.ACTIVE_SCENE.add_child(clouds)
        uniques.ACTIVE_SCENE.add_children(idle_props)
        uniques.ACTIVE_SCENE.add_children(props)
        uniques.ACTIVE_SCENE.add_child(self._player)
        uniques.ACTIVE_SCENE.add_children(doors)

    def _on_scene_end(self) -> None:
        if self.on_ended:
            # Pass a package containing all useful information for the next room.
            self.on_ended(self._bundle)

    def _on_scene_start(self) -> None:
        if self._player is not None:
            self._player.enable_controls()

    def on_door_triggered(self, entered: bool, bundle: dict):
        if entered:
            if uniques.ACTIVE_SCENE is not None:
                uniques.ACTIVE_SCENE.end()
                self._bundle = bundle

            if self._player is not None:
                self._player.disable_controls()

    def draw(self) -> None:
        if uniques.ACTIVE_SCENE is not None:
            uniques.ACTIVE_SCENE.draw()

    def update(self, dt) -> None:
        if uniques.ACTIVE_SCENE is not None:
            uniques.ACTIVE_SCENE.update(dt)

    def delete(self) -> None:
        if uniques.ACTIVE_SCENE is not None:
            uniques.ACTIVE_SCENE.delete()