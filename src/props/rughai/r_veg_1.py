from typing import Optional
import pyglet

from engine.node import PositionNode
from engine.sprite_node import SpriteNode
from engine.utils import animation_set_anchor

class RVeg1(PositionNode):
    def __init__(
        self,
        x: int = 0,
        y: int = 0,
        z: float = 0,
        scaling: int = 1,
        batch: Optional[pyglet.graphics.Batch] = None
    ) -> None:
        super().__init__(x, y, z)

        self.__scaling = scaling

        self.__idle_animation = pyglet.resource.animation("sprites/rughai/prop/veg_1/veg_1_idle.gif")
        animation_set_anchor(
            animation = self.__idle_animation,
            x = self.__idle_animation.get_max_width() / 2,
            y = 0
        )

        self.__sprite = SpriteNode(
            resource = self.__idle_animation,
            batch = batch,
            x = x,
            y = y,
            scaling = scaling,
            on_animation_end = lambda : None
        )

    def draw(self) -> None:
        self.__sprite.draw()

    def delete(self) -> None:
        self.__sprite.delete()