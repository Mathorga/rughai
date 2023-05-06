import random
from typing import Optional
import pyglet

from engine.node import PositionNode
from engine.sprite_node import SpriteNode
from engine.utils import animation_set_anchor

class RGrass0(PositionNode):
    def __init__(
        self,
        x: float = 0,
        y: float = 0,
        z: float = 0,
        scaling: int = 1,
        batch: Optional[pyglet.graphics.Batch] = None
    ) -> None:
        super().__init__(x, y, z)

        self.__scaling = scaling

        self.__idle_0_anim = pyglet.resource.image("sprites/rughai/prop/grass_0/grass_0_idle_0.png")
        self.__idle_1_anim = pyglet.resource.animation("sprites/rughai/prop/grass_0/grass_0_idle_1.gif")
        self.__idle_0_anim.anchor_x = self.__idle_0_anim.width / 2
        self.__idle_0_anim.anchor_y = 0
        animation_set_anchor(
            animation = self.__idle_1_anim,
            x = self.__idle_1_anim.get_max_width() / 2,
            y = 0
        )

        self.__sprite = SpriteNode(
            resource = self.__idle_0_anim,
            x = x,
            y = y,
            scaling = scaling,
            on_animation_end = self.update_animation,
            batch = batch
        )

    def delete(self) -> None:
        self.__sprite.delete()

    def update_animation(self):
        if random.random() < 0.1:
            self.__sprite.set_image(self.__idle_1_anim)
        else:
            self.__sprite.set_image(self.__idle_0_anim)