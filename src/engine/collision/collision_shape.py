import pyglet
import pyglet.math as pm

from engine.node import PositionNode
from engine.shapes.circle_node import CircleNode
from engine.shapes.line_node import LineNode
from engine.shapes.rect_node import RectNode
from engine.shapes.shape_node import ShapeNode
import engine.utils.utils as utils
from engine.settings import SETTINGS, Keys

COLLIDING_COLOR = (0x7FF, 0x7F, 0x7F, 0x7F)
FREE_COLOR = (0x7F, 0xFF, 0xFF, 0x7F)

class CollisionShape(PositionNode):
    def __init__(
        self,
        x: float = 0.0,
        y: float = 0.0,
        z: float = 0.0,
        color: tuple[int, int, int, int] = FREE_COLOR
    ) -> None:
        super().__init__(x, y, z)

        # Velocity components.
        self.velocity_x = 0.0
        self.velocity_y = 0.0
        self.color: tuple[int, int, int, int] = color

        self.render_shape: ShapeNode | None = None
        self.velocity_shape: LineNode | None = None

    def set_position(
        self,
        position: tuple[float, float],
        z: float | None = None
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
        velocity: tuple[float, float]
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
        velocity: tuple[float, float]
    ) -> None:
        """
        Sums the provided velocity to any already there.
        """

        self.velocity_x += velocity[0]
        self.velocity_y += velocity[1]

        if self.velocity_shape is not None:
            self.velocity_shape.set_delta((self.velocity_shape.delta_x + velocity[0], self.velocity_shape.delta_y + velocity[1]))

    def set_color(self, color: tuple[int, int, int, int]) -> None:
        self.color = color

    def swept_collide(self, other) -> utils.CollisionHit | None:
        return None

    def overlap(self, _other) -> bool:
        return False

    def collide(self, _other) -> tuple[float, float]:
        return (0.0, 0.0)

    def delete(self) -> None:
        if self.render_shape is not None:
            self.render_shape.delete()

class CollisionRect(CollisionShape):
    def __init__(
        self,
        x: float = 0.0,
        y: float = 0.0,
        z: float = 0.0,
        width: int = 0,
        height: int = 0,
        anchor_x: int = 0,
        anchor_y: int = 0,
        color: tuple[int, int, int, int] = FREE_COLOR,
        batch: pyglet.graphics.Batch | None = None
    ) -> None:
        super().__init__(x, y, z, color)

        self.width: int = width
        self.height: int = height
        self.anchor_x: int = anchor_x
        self.anchor_y: int = anchor_y

        if SETTINGS[Keys.DEBUG] and SETTINGS[Keys.SHOW_COLLISIONS]:
            self.render_shape = RectNode(
                x = x,
                y = y,
                width = width,
                height = height,
                anchor_x = anchor_x,
                anchor_y = anchor_y,
                color = self.color,
                batch = batch
            )

            self.velocity_shape = LineNode(
                x = x,
                y = y,
                delta_x = self.velocity_x,
                delta_y = self.velocity_y,
                color = FREE_COLOR,
                batch = batch
            )

    def get_collision_bounds(self):
        return (
            self.x - self.anchor_x,
            self.y - self.anchor_y,
            self.width,
            self.height
        )

    def swept_collide(self, other) -> utils.CollisionHit | None:
        return utils.sweep_rect_rect(
            collider = utils.Rect(
                center = pm.Vec2(self.x - self.anchor_x + self.width / 2, self.y - self.anchor_y + self.height / 2),
                half_size = pm.Vec2(self.width / 2, self.height / 2)
            ),
            rect = utils.Rect(
                center = pm.Vec2(other.x - other.anchor_x + other.width / 2, other.y - other.anchor_y + other.height / 2),
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

    def collide(self, other) -> tuple[float, float]:
        if isinstance(other, CollisionRect):
            # Rect/rect collision.
            return utils.rect_rect_solve(
                *self.get_collision_bounds(),
                *other.get_collision_bounds()
            )
        else:
            # Other.
            return (0, 0)

    def set_color(self, color: tuple[int, int, int, int]) -> None:
        super().set_color(color = color)

        # Set render shape color.
        if self.render_shape is not None:
            self.render_shape.set_color(color = color[:-1])

class CollisionCircle(CollisionShape):
    def __init__(
        self,
        x: float = 0,
        y: float = 0,
        z: float = 0.0,
        radius: int = 1,
        batch: pyglet.graphics.Batch | None = None
    ) -> None:
        super().__init__(x, y, z)

        self.radius = radius
        self.width = radius * 2
        self.height = radius * 2


        if SETTINGS[Keys.DEBUG] and SETTINGS[Keys.SHOW_COLLISIONS]:
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

    def swept_collide(self, other) -> utils.CollisionHit | None:
        # TODO
        # https://ericleong.me/research/circle-circle/#dynamic-static-circle-collision-detection
        return None

    def collide(self, other) -> tuple[float, float]:
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