from typing import Optional
import pyglet

from engine.collision.collision_manager import CollisionManager
from engine.collision.collision_node import CollisionNode, CollisionType
from engine.collision.collision_shape import CollisionRect
from engine.node import PositionNode

class WallNode(PositionNode):
    def __init__(
        self,
        collision_manager: CollisionManager,
        x: float = 0,
        y: float = 0,
        width: int = 8,
        height: int = 8,
        scaling: int = 1,
        batch: Optional[pyglet.graphics.Batch] = None
    ) -> None:
        super().__init__(x, y)

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
                    width = width,
                    height = height,
                    scaling = scaling,
                    batch = batch
                )
            ]
        )
        collision_manager.add_collider(self.__collider)

    def delete(self) -> None:
        self.__collider.delete()