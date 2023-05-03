from typing import Optional
import pyglet

from engine.collision.collision_manager import CollisionManager
from engine.collision.collision_node import CollisionNode, CollisionType
from engine.collision.collision_shape import CollisionRect
from engine.node import PositionNode
from engine.sprite_node import SpriteNode
from engine.utils import animation_set_anchor

class RTreeM(PositionNode):
    def __init__(
        self,
        collision_manager: CollisionManager,
        x: float = 0,
        y: float = 0,
        z: float = 0,
        scaling: int = 1,
        batch: Optional[pyglet.graphics.Batch] = None
    ) -> None:
        super().__init__(x, y, z)

        self.__scaling = scaling

        self.__idle_animation = pyglet.resource.animation("sprites/rughai/prop/tree_m/tree_m_idle_1.gif")
        animation_set_anchor(
            animation = self.__idle_animation,
            x = self.__idle_animation.get_max_width() / 2,
            y = 0
        )

        self.__sprite = SpriteNode(
            resource = self.__idle_animation,
            x = x,
            y = y,
            scaling = scaling,
            on_animation_end = lambda : None,
            batch = batch
        )

        # Collider.
        self.__collider = CollisionNode(
            x = x,
            y = y,
            type = CollisionType.STATIC,
            tag = "player",
            shapes = [
                CollisionRect(
                    x = x,
                    y = y,
                    width = 8,
                    height = 8,
                    anchor_x = 4,
                    anchor_y = 0,
                    scaling = scaling,
                    batch = batch
                )
            ]
        )
        collision_manager.add_collider(self.__collider)

    def draw(self) -> None:
        self.__sprite.draw()

    def delete(self) -> None:
        self.__sprite.delete()