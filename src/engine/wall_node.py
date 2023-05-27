from typing import Optional
import pyglet

from engine import controllers
from engine.collision.collision_controller import CollisionController
from engine.collision.collision_node import CollisionNode, CollisionType
from engine.collision.collision_shape import CollisionCircle, CollisionRect
from engine.node import PositionNode

class ColumnNode(PositionNode):
    def __init__(
        self,
        x: float = 0,
        y: float = 0,
        radius: int = 1,
        scaling: int = 1,
        batch: Optional[pyglet.graphics.Batch] = None
    ) -> None:
        super().__init__(x, y)

        # Collider.
        self.__collider = CollisionNode(
            x = x,
            y = y,
            collision_type = CollisionType.STATIC,
            tags = ["player"],
            shapes = [
                CollisionCircle(
                    x = x,
                    y = y,
                    radius = radius,
                    scaling = scaling,
                    batch = batch
                )
            ]
        )
        controllers.collision_controller.add_collider(self.__collider)

    def delete(self) -> None:
        self.__collider.delete()

class WallNode(PositionNode):
    def __init__(
        self,
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
            collision_type = CollisionType.STATIC,
            tags = ["player"],
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
        controllers.collision_controller.add_collider(self.__collider)

    def delete(self) -> None:
        self.__collider.delete()