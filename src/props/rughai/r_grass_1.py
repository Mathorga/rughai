from typing import Optional
import pyglet

from engine.node import PositionNode
from engine.sprite_node import SpriteNode
from engine.renderer import Renderer
from engine.utils import animation_set_anchor

class RGrass1(PositionNode):
    def __init__(
        self,
        x: int = 0,
        y: int = 0,
        z: float = 0,
        scaling: int = 1,
        ui: bool = False
    ) -> None:
        super().__init__(x, y, z)

        self.__scaling = scaling

        self.__idle_animation = pyglet.resource.animation("sprites/rughai/prop/grass_1/grass_1_idle_1.gif")
        animation_set_anchor(
            animation = self.__idle_animation,
            x = self.__idle_animation.get_max_width() / 2,
            y = 0
        )

        self.__sprite = SpriteNode(
            resource = self.__idle_animation,
            ui = ui,
            x = x,
            y = y,
            scaling = scaling,
            on_animation_end = lambda : None
        )

    def draw(self) -> None:
        self.__sprite.draw()

    def delete(self) -> None:
        self.__sprite.delete()