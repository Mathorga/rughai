from typing import Optional
import pyglet

from constants import collision_tags
from engine import controllers
from engine.collision.collision_node import CollisionNode, CollisionType
from engine.collision.collision_shape import CollisionCircle, CollisionRect
from engine.node import PositionNode

class ColumnNode(PositionNode):
    def __init__(
        self,
        x: float = 0,
        y: float = 0,
        radius: int = 1,
        batch: Optional[pyglet.graphics.Batch] = None
    ) -> None:
        super().__init__(x, y)

        # Collider.
        self.__collider = CollisionNode(
            x = x,
            y = y,
            collision_type = CollisionType.STATIC,
            tags = [collision_tags.PLAYER_COLLISION],
            shapes = [
                CollisionCircle(
                    x = x,
                    y = y,
                    radius = radius,
                    batch = batch
                )
            ]
        )
        controllers.COLLISION_CONTROLLER.add_collider(self.__collider)

    def delete(self) -> None:
        self.__collider.delete()

class WallNode(PositionNode):
    def __init__(
        self,
        x: float = 0,
        y: float = 0,
        width: int = 8,
        height: int = 8,
        batch: Optional[pyglet.graphics.Batch] = None
    ) -> None:
        super().__init__(x, y)

        # Collider.
        self.__collider = CollisionNode(
            x = x,
            y = y,
            collision_type = CollisionType.STATIC,
            tags = [collision_tags.PLAYER_COLLISION],
            shapes = [
                CollisionRect(
                    x = x,
                    y = y,
                    width = width,
                    height = height,
                    batch = batch
                )
            ]
        )
        controllers.COLLISION_CONTROLLER.add_collider(self.__collider)

    def delete(self) -> None:
        self.__collider.delete()