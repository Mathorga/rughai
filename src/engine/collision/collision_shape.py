from typing import Optional, Tuple
import pyglet
import pyglet.math as pm

from engine.node import PositionNode
from engine.shapes.circle_node import CircleNode
from engine.shapes.line_node import LineNode
from engine.shapes.rect_node import RectNode
from engine.shapes.shape_node import ShapeNode
import engine.utils as utils
from engine.settings import SETTINGS, Builtins


COLLIDING_COLOR = (0x7FF, 0x7F, 0x7F, 0x7F)
FREE_COLOR = (0x7F, 0xFF, 0xFF, 0x7F)

class CollisionShape(PositionNode):
    def __init__(
        self,
        x: float = 0,
        y: float = 0,
        z: float = 0.0
    ) -> None:
        super().__init__(x, y, z)

        # Velocity components.
        self.velocity_x = 0.0
        self.velocity_y = 0.0

        self.render_shape: Optional[ShapeNode] = None
        self.velocity_shape: Optional[LineNode] = None

    def set_position(
        self,
        position: Tuple[float, float],
        z: Optional[float] = None
    ) -> None:
        """
        Sets the shape position.
        """
        super().set_position(position, z)

        if self.render_shape is not None:
            self.render_shape.set_position(position)

        if self.velocity_shape is not None:
            self.velocity_shape.set_position(position)

    def set_velocity(
        self,
        velocity: Tuple[float, float]
    ) -> None:
        """
        Sets the shape velocity.
        """

        self.velocity_x = velocity[0]
        self.velocity_y = velocity[1]

        if self.velocity_shape is not None:
            self.velocity_shape.set_delta(velocity)

    def put_velocity(
        self,
        velocity: Tuple[float, float]
    ) -> None:
        """
        Sums the provided velocity to any already there.
        """
        self.velocity_x += velocity[0]
        self.velocity_y += velocity[1]

        if self.velocity_shape is not None:
            self.velocity_shape.set_delta((self.velocity_shape.delta_x + velocity[0], self.velocity_shape.delta_y + velocity[1]))

    def swept_collide(self, other) -> utils.CollisionSweep:
        return utils.CollisionSweep()

    def overlap(self, _other) -> bool:
        return False

    def collide(self, _other) -> Tuple[float, float]:
        return (0.0, 0.0)

    def delete(self) -> None:
        if self.render_shape is not None:
            self.render_shape.delete()

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
        batch: Optional[pyglet.graphics.Batch] = None
    ) -> None:
        super().__init__(x, y, z)

        self.width = width
        self.height = height
        self.anchor_x = anchor_x
        self.anchor_y = anchor_y

        if SETTINGS[Builtins.DEBUG] and SETTINGS[Builtins.SHOW_COLLISIONS]:
            self.render_shape = RectNode(
                x = x,
                y = y,
                width = width,
                height = height,
                anchor_x = anchor_x,
                anchor_y = anchor_y,
                color = (0x7F, 0xFF, 0xFF, 0x7F),
                batch = batch
            )

            self.velocity_shape = LineNode(
                x = x,
                y = y,
                delta_x = self.velocity_x,
                delta_y = self.velocity_y,
                color = (0xFF, 0x7F, 0xFF, 0x7F),
                batch = batch
            )

    def get_collision_bounds(self):
        return (
            self.x - self.anchor_x,
            self.y - self.anchor_y,
            self.width,
            self.height
        )

    def swept_collide(self, other) -> utils.CollisionSweep:
        return utils.sweep_aabb_aabb(
            collider = utils.AABB(
                center = pm.Vec2(self.x - self.anchor_x + self.width / 2, self.y - self.anchor_y + self.height / 2),
                half_size = pm.Vec2(self.width / 2, self.height / 2)
            ),
            rect = utils.AABB(
                center = pm.Vec2(other.x + other.width / 2, other.y + other.height / 2),
                half_size = pm.Vec2(other.width / 2, other.height / 2)
            ),
            delta = pm.Vec2(self.velocity_x, self.velocity_y)
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
        batch: Optional[pyglet.graphics.Batch] = None
    ) -> None:
        super().__init__(x, y, z)

        self.radius = radius
        self.width = radius * 2
        self.height = radius * 2


        if SETTINGS[Builtins.DEBUG] and SETTINGS[Builtins.SHOW_COLLISIONS]:
            self.render_shape = CircleNode(
                x = x,
                y = y,
                radius = radius,
                color = (0x7F, 0xFF, 0xFF, 0x7F),
                batch = batch
            )

    def overlap(self, other) -> bool:
        if isinstance(other, CollisionRect):
            # Circle/rect overlap.
            return utils.circle_rect_check(
                self.x,
                self.y,
                self.radius,
                *other.get_collision_bounds()
            )
        elif isinstance(other, CollisionCircle):
            # Circle/circle overlap.
            return utils.circle_circle_check(
                self.x,
                self.y,
                self.radius,
                other.x,
                other.y,
                other.radius
            )
        else:
            # Other.
            return False

    def collide(self, other) -> Tuple[float, float]:
        if isinstance(other, CollisionRect):
            # Circle/rect collision.
            return utils.circle_rect_solve(
                self.x,
                self.y,
                self.radius,
                *other.get_collision_bounds()
            )
        elif isinstance(other, CollisionCircle):
            # Circle/circla collision.
            return utils.circle_circle_solve(
                self.x,
                self.y,
                self.radius,
                other.x,
                other.y,
                other.radius
            )
        else:
            # Other.
            return (0, 0)