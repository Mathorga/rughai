import random
from typing import Optional
import pyglet
from engine.collision.collision_shape import CollisionRect

from engine.node import PositionNode
from engine.sprite_node import SpriteNode
from engine.utils import animation_set_anchor
from props.prop_node import PropNode

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

        self.__idle_0_anim = pyglet.image.Animation.from_image_sequence([pyglet.resource.image("sprites/rughai/prop/grass_0/grass_0_idle_0.png")], 1.0)
        self.__idle_1_anim = pyglet.resource.animation("sprites/rughai/prop/grass_0/grass_0_idle_1.gif")
        animation_set_anchor(
            animation = self.__idle_1_anim,
            x = self.__idle_1_anim.get_max_width() / 2,
            y = 0
        )
        animation_set_anchor(
            animation = self.__idle_0_anim,
            x = self.__idle_0_anim.get_max_width() / 2,
            y = 0
        )

        self.prop_node = PropNode(
            x = x,
            y = y,
            z = z,
            scaling = scaling,
            main_idle_anim = self.__idle_0_anim,
            sec_idle_anims = [
                self.__idle_1_anim
            ],
            batch = batch
        )

    def update(self, dt: int) -> None:
        self.prop_node.update(dt)

    def delete(self) -> None:
        self.prop_node.delete()