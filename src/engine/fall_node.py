import pyglet

from engine import controllers
from engine.collision.collision_node import CollisionNode, CollisionType
from engine.collision.collision_shape import CollisionCircle, CollisionRect
from engine.node import PositionNode

FALL_COLOR: tuple[int, int, int, int] = (0xFF, 0x44, 0x00, 0x7F)

class FallNode(PositionNode):
    def __init__(
        self,
        x: float = 0,
        y: float = 0,
        width: int = 8,
        height: int = 8,
        tags: list[str] | None = None,
        batch: pyglet.graphics.Batch | None = None
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
            sensor = True,
            color = FALL_COLOR,
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