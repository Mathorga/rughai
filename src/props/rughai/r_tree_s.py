import random
from typing import Optional
import pyglet

from engine.collision.collision_manager import CollisionManager
from engine.collision.collision_node import CollisionNode, CollisionType
from engine.collision.collision_shape import CollisionRect
from engine.node import PositionNode
from engine.sprite_node import SpriteNode
from engine.utils import animation_set_anchor

class RTreeS(PositionNode):
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

        self.__idle_0_anim = pyglet.image.Animation.from_image_sequence([pyglet.resource.image("sprites/rughai/prop/tree_s/tree_s_idle_0.png")], 1.0)
        self.__idle_1_anim = pyglet.resource.animation("sprites/rughai/prop/tree_s/tree_s_idle_1.gif")
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

        self.__sprite = SpriteNode(
            resource = self.__idle_0_anim,
            x = x,
            y = y,
            scaling = scaling,
            on_animation_end = self.update_animation,
            batch = batch
        )

        # Collider.
        self.__collider = CollisionNode(
            x = x,
            y = y,
            type = CollisionType.STATIC,
            tags = ["player"],
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

    def update_animation(self):
        if random.random() < 0.05:
            self.__sprite.set_image(self.__idle_1_anim)
        else:
            self.__sprite.set_image(self.__idle_0_anim)