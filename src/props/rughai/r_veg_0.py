from typing import Optional, Tuple
import pyglet

from amonite.node import PositionNode
from amonite.utils.utils import set_animation_anchor
from props.idle_prop_node import PropNode

class RVeg0(PositionNode):
    def __init__(
        self,
        x: float = 0,
        y: float = 0,
        z: float = 0,
        batch: Optional[pyglet.graphics.Batch] = None
    ) -> None:
        super().__init__(x, y, z)

        self.__idle_0_anim = pyglet.resource.animation("sprites/prop/rughai/veg_0/veg_0_idle_0.gif")
        self.__idle_1_anim = pyglet.resource.animation("sprites/prop/rughai/veg_0/veg_0_idle_1.gif")
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
            batch = batch
        )

    def set_position(self, position: tuple[float, float], z: Optional[float] = None):
        super().set_position(position, z)
        self.prop_node.set_position(position, z)

    def update(self, dt: int) -> None:
        self.prop_node.update(dt)

    def delete(self) -> None:
        self.prop_node.delete()