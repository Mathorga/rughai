from typing import List, Optional, Tuple
import pyglet

from engine import controllers
from engine.collision.collision_node import CollisionNode, CollisionType
from engine.collision.collision_shape import CollisionCircle, CollisionRect
from engine.node import PositionNode

WALL_COLOR: Tuple[int, int, int, int] = (0xFF, 0x7F, 0xFF, 0x7F)

class WallNode(PositionNode):
    def __init__(
        self,
        x: float = 0,
        y: float = 0,
        width: int = 8,
        height: int = 8,
        tags: Optional[List[str]] = None,
        batch: Optional[pyglet.graphics.Batch] = None
    ) -> None:
        super().__init__(x, y)

        self.tags = tags if tags is not None else []
        self.width = width
        self.height = height

        # Collider.
        self.__collider = CollisionNode(
            x = x,
            y = y,
            collision_type = CollisionType.STATIC,
            passive_tags = self.tags,
            color = WALL_COLOR,
            shape = CollisionRect(
                x = x,
                y = y,
                width = width,
                height = height,
                batch = batch
            )
        )
        controllers.COLLISION_CONTROLLER.add_collider(self.__collider)

    def delete(self) -> None:
        self.__collider.delete()