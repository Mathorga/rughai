import random
from typing import List, Optional
import pyglet

from engine.collision.collision_manager import CollisionManager
from engine.collision.collision_node import CollisionNode, CollisionType
from engine.collision.collision_shape import CollisionShape
from engine.node import PositionNode
from engine.sprite_node import SpriteNode

class PropNode(PositionNode):
    def __init__(
        self,
        main_idle_anim: pyglet.image.animation.Animation,
        # Proportion between main and secondary animations.
        main_to_sec: float = 0.95,
        sec_idle_anims: List[pyglet.image.animation.Animation] = [],
        collision_manager: Optional[CollisionManager] = None,
        x: float = 0,
        y: float = 0,
        z: float = 0,
        scaling: int = 1,
        collision_shapes: List[CollisionShape] = [],
        batch: Optional[pyglet.graphics.Batch] = None
    ) -> None:
        super().__init__(x, y, z)

        # Make sure at least one idle animation is provided.
        assert len(sec_idle_anims) > 0

        self.main_idle_anim = main_idle_anim
        self.main_to_sec = main_to_sec

        self.__scaling = scaling

        self.sec_idle_anims = sec_idle_anims

        # Sprite.
        self.__sprite = SpriteNode(
            resource = sec_idle_anims[0],
            x = x,
            y = y,
            scaling = scaling,
            on_animation_end = self.update_animation,
            batch = batch
        )

        self.__collider: Optional[CollisionNode] = None
        if len(collision_shapes) > 0:
            assert collision_manager is not None

            # Collider.
            self.__collider = CollisionNode(
                x = x,
                y = y,
                type = CollisionType.STATIC,
                tags = ["player"],
                shapes = collision_shapes
            )
            collision_manager.add_collider(self.__collider)

    def delete(self) -> None:
        self.__sprite.delete()

        if self.__collider is not None:
            self.__collider.delete()

    def update_animation(self):
        if random.random() < self.main_to_sec:
            self.__sprite.set_image(self.main_idle_anim)
        else:
            self.__sprite.set_image(self.sec_idle_anims[random.randint(0, len(self.sec_idle_anims) - 1)])