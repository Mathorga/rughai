from typing import Callable, Optional
import pyglet
from constants import scenes

from engine.node import Node
from engine.scene_node import SceneNode
from player_node import PlayerNode


class PlayableSceneNode(Node):
    def __init__(
        self,
        window: pyglet.window.Window,
        view_width: int,
        view_height: int,
        bundle: Optional[dict] = None,
        on_ended: Optional[Callable[[dict], None]] = None
    ) -> None:
        super().__init__()

        self._window = window
        self._on_ended = on_ended

        # The bundle containing instructions for the next scene.
        self._bundle: dict

        scenes.ACTIVE_SCENE: Optional[SceneNode]

        # Player.
        self._player: PlayerNode

    def on_door_triggered(self, entered: bool, bundle: dict):
        if entered:
            if scenes.ACTIVE_SCENE is not None:
                scenes.ACTIVE_SCENE.end()
                self._bundle = bundle

            if self._player is not None:
                self._player.disable_controls()

    def _on_scene_end(self) -> None:
        if self._on_ended:
            # Pass a package containing all useful information for the next room.
            self._on_ended(self._bundle)

    def _on_scene_start(self) -> None:
        if self._player is not None:
            self._player.enable_controls()

    def draw(self) -> None:
        if scenes.ACTIVE_SCENE is not None:
            scenes.ACTIVE_SCENE.draw()

    def update(self, dt) -> None:
        if scenes.ACTIVE_SCENE is not None:
            scenes.ACTIVE_SCENE.update(dt)

    def delete(self) -> None:
        if scenes.ACTIVE_SCENE is not None:
            scenes.ACTIVE_SCENE.delete()