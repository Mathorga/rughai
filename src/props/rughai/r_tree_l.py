from typing import Optional, Tuple
import pyglet

from engine.collision.collision_shape import CollisionRect
from engine.node import PositionNode
from engine.utils import set_animation_anchor
from props.prop_node import PropNode

class RTreeL(PositionNode):
    def __init__(
        self,
        x: float = 0,
        y: float = 0,
        z: float = 0,
        batch: Optional[pyglet.graphics.Batch] = None
    ) -> None:
        super().__init__(x, y, z)

        self.__idle_0_anim = pyglet.resource.animation("sprites/prop/rughai/tree_l/tree_l_idle_0.gif")
        self.__idle_1_anim = pyglet.resource.animation("sprites/prop/rughai/tree_l/tree_l_idle_1.gif")
        set_animation_anchor(
            animation = self.__idle_1_anim,
            x = self.__idle_1_anim.get_max_width() / 2,
            y = 0
        )
        set_animation_anchor(
            animation = self.__idle_0_anim,
            x = self.__idle_0_anim.get_max_width() / 2,
            y = 0
        )

        self.prop_node = PropNode(
            x = x,
            y = y,
            z = z,
            main_idle_anim = self.__idle_0_anim,
            sec_idle_anims = [
                self.__idle_1_anim
            ],
            collision_shapes = [
                CollisionRect(
                    x = x,
                    y = y,
                    width = 8,
                    height = 8,
                    anchor_x = 4,
                    anchor_y = 0,
                    batch = batch
                )
            ],
            batch = batch
        )

    def set_position(self, position: Tuple[float, float], z: Optional[float] = None):
        super().set_position(position, z)
        self.prop_node.set_position(position, z)

    def update(self, dt: int) -> None:
        self.prop_node.update(dt)

    def delete(self) -> None:
        self.prop_node.delete()