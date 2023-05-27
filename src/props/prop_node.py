import random
from typing import List, Optional
import pyglet

from engine import controllers
from engine.collision.collision_node import CollisionNode, CollisionType
from engine.collision.collision_shape import CollisionShape
from engine.node import PositionNode
from engine.sprite_node import SpriteNode

class PropNode(PositionNode):
    def __init__(
        self,
        main_idle_anim: pyglet.image.animation.Animation,
        # Proportion between main and secondary animations.
        main_to_sec: float = 0.99,
        # Animation duration.
        anim_duration: float = 1.0,
        sec_idle_anims: List[pyglet.image.animation.Animation] = [],
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
        self.__anim_duration = anim_duration
        self.__elapsed_anim_time = 0.0

        self.sec_idle_anims = sec_idle_anims

        # Sprite.
        self._sprite = SpriteNode(
            resource = main_idle_anim,
            x = x,
            y = y,
            scaling = scaling,
            batch = batch
        )

        self.__collider: Optional[CollisionNode] = None
        if len(collision_shapes) > 0:
            # Collider.
            self.__collider = CollisionNode(
                x = x,
                y = y,
                collision_type = CollisionType.STATIC,
                tags = ["player"],
                shapes = collision_shapes
            )
            controllers.collision_controller.add_collider(self.__collider)

    def update(self, dt: float) -> None:
        self.__elapsed_anim_time += dt
        if self.__elapsed_anim_time > self.__anim_duration and self._sprite.get_frame_index() <= 0:
            self.update_animation()
            self.__elapsed_anim_time = 0.0

    def delete(self) -> None:
        self._sprite.delete()

        if self.__collider is not None:
            self.__collider.delete()

    def update_animation(self):
        if random.random() < self.main_to_sec:
            self._sprite.set_image(self.main_idle_anim)
        else:
            self._sprite.set_image(self.sec_idle_anims[random.randint(0, len(self.sec_idle_anims) - 1)])