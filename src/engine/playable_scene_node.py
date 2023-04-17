from typing import Callable, Optional
import pyglet

from engine.collision_manager import CollisionManager
from engine.input_controller import InputController
from engine.node import Node, PositionNode
from engine.scene_node import SceneNode
from player_node import PlayerNode


class PlayableSceneNode(Node):
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
        self._input_controller = input_controller

        # The bundle containing instructions for the next scene.
        self._bundle: dict

        self._scene: Optional[SceneNode]

        # Player.
        self._player: PlayerNode

    def delete(self) -> None:
        if self._scene is not None:
            self._scene.delete()

    def on_door_triggered(self, entered: bool, bundle: dict):
        if entered:
            if self._scene is not None:
                self._scene.end()
                self._bundle = bundle

            if self._player is not None:
                self._player.disable_controls()

    def _on_scene_end(self) -> None:
        if self._on_ended:
            # Pass a package containing all useful information for the next room.
            self._on_ended(self._bundle)

    def draw(self) -> None:
        if self._scene is not None:
            self._scene.draw()

    def update(self, dt) -> None:
        if self._scene is not None:
            self._scene.update(dt)
