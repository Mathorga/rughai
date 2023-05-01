from typing import Callable, Optional
import pyglet

from engine.collision.collision_manager import CollisionManager
from engine.input_controller import InputController
from engine.playable_scene_node import PlayableSceneNode


class MapSceneNode(PlayableSceneNode):
    """
    Class defining a generic playable scene. It contains a player and accepts a prop placement file as input for placing props.
    """
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
    ) -> None:
        super().__init__(
            window,
            collision_manager,
            input_controller,
            view_width,
            view_height,
            scaling,
            bundle,
            on_ended
        )