from typing import Callable, Optional
import pyglet

from engine.collision_manager import CollisionManager
from engine.input_controller import InputController
from engine.node import Node
from engine.scene_node import SceneNode

class SceneManagerNode(Node):
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
        super().__init__()

        self._window = window
        self._on_ended = on_ended
        self._collision_manager = collision_manager
        self._bundle = bundle

        self._scene: Optional[SceneNode]


    def clear_scene(self) -> None:
        if self._scene is not None:
            self._scene.clear_children()

    def draw(self) -> None:
        if self._scene is not None:
            self._scene.draw()

    def update(self, dt) -> None:
        if self._scene is not None:
            self._scene.update(dt)