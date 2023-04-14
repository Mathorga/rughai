from typing import Optional
import pyglet

from engine.node import PositionNode
from engine.sprite_node import SpriteNode
from engine.sprites_manager import SpritesManager
from engine.utils import animation_set_anchor

class RTreeS(PositionNode):
    def __init__(
        self,
        sprites_manager: SpritesManager,
        x: int = 0,
        y: int = 0,
        z: float = 0,
        scaling: int = 1,
        batch: Optional[pyglet.graphics.Batch] = None
    ) -> None:
        super().__init__(x, y, z)

        self.__scaling = scaling

        self.__idle_animation = pyglet.resource.animation("sprites/rughai/prop/tree_s/tree_s_idle_1.gif")
        animation_set_anchor(
            animation = self.__idle_animation,
            x = self.__idle_animation.get_max_width() / 2,
            y = 0
        )

        self.__sprite = SpriteNode(
            resource = self.__idle_animation,
            sprites_manager = sprites_manager,
            x = x,
            y = y,
            scaling = scaling,
            on_animation_end = lambda : None
        )

    def draw(self) -> None:
        self.__sprite.draw()