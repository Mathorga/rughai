from typing import Optional, Tuple
import pyglet
from engine.circle_node import CircleNode

from engine.node import PositionNode
from engine.rect_node import RectNode
import engine.utils as utils

class CollisionShape(PositionNode):
    def __init__(
        self,
        x: float = 0,
        y: float = 0,
        z: float = 0.0
    ) -> None:
        super().__init__(x, y, z)

    def overlap(self, other) -> bool:
        return False

    def collide(self, other) -> Tuple[float, float]:
        return (0.0, 0.0)

class CollisionRect(CollisionShape):
    def __init__(
        self,
        x: float = 0,
        y: float = 0,
        z: float = 0.0,
        width: int = 0,
        height: int = 0,
        anchor_x: float = 0,
        anchor_y: float = 0,
        scaling: int = 1,
        batch: Optional[pyglet.graphics.Batch] = None
    ) -> None:
        super().__init__(x, y, z)

        self.width = width
        self.height = height
        self.anchor_x = anchor_x
        self.anchor_y = anchor_y
        self.scaling = scaling

        self.render_shape = RectNode(
            x = x,
            y = y,
            width = width,
            height = height,
            scaling = scaling,
            anchor_x = anchor_x,
            anchor_y = anchor_y,
            color = (0x7F, 0xFF, 0xFF, 0x7F),
            batch = batch
        )

    def set_position(
        self,
        position: Tuple[int, int],
        z: Optional[float] = None
    ) -> None:
        self.x = position[0]
        self.y = position[1]
        self.render_shape.set_position(position)

    def get_collision_bounds(self):
        return (
            self.x - self.anchor_x,
            self.y - self.anchor_y,
            self.width,
            self.height
        )

    def overlap(self, other) -> bool:
        if isinstance(other, CollisionRect):
            # Rect/rect overlap.
            return utils.rect_rect_check(
                *self.get_collision_bounds(),
                *other.get_collision_bounds()
            )
        else:
            # Other.
            return False

    def collide(self, other) -> Tuple[float, float]:
        if isinstance(other, CollisionRect):
            # Rect/rect collision.
            return utils.rect_rect_solve(
                *self.get_collision_bounds(),
                *other.get_collision_bounds()
            )
        else:
            # Other.
            return (0, 0)

class CollisionCircle(CollisionShape):
    def __init__(
        self,
        x: float = 0,
        y: float = 0,
        z: float = 0.0,
        radius: int = 1,
        scaling: int = 1,
        batch: Optional[pyglet.graphics.Batch] = None
    ) -> None:
        super().__init__(x, y, z)

        self.radius = radius
        self.width = radius * 2
        self.height = radius * 2
        self.scaling = scaling

        self.render_shape = CircleNode(
            x = x,
            y = y,
            z = z,
            radius = radius,
            color = (0x7F, 0xFF, 0xFF, 0x7F),
            scaling = scaling,
            batch = batch
        )

    def set_position(
        self,
        position: Tuple[int, int],
        z: Optional[float] = None
    ) -> None:
        self.x = position[0]
        self.y = position[1]
        self.render_shape.set_position(position)

    def overlap(self, other) -> bool:
        if isinstance(other, CollisionRect):
            # Rect/rect overlap.
            return utils.circle_rect_check(
                self.x,
                self.y,
                self.radius,
                *other.get_collision_bounds()
            )
        else:
            # Other.
            return False

    def collide(self, other) -> Tuple[float, float]:
        if isinstance(other, CollisionRect):
            # Rect/rect collision.
            return utils.circle_rect_solve(
                self.x,
                self.y,
                self.radius,
                *other.get_collision_bounds()
            )
        else:
            # Other.
            return (0, 0)