from enum import Enum
from typing import Callable, Optional

from engine.collision.collision_shape import CollisionShape
from engine.node import PositionNode
from engine.utils.utils import CollisionHit

COLLIDER_COLOR: tuple[int, int, int, int] = (0x7F, 0xFF, 0xFF, 0x7F)
SENSOR_COLOR: tuple[int, int, int, int] = (0x7F, 0xFF, 0x7F, 0x7F)

class CollisionType(Enum):
    STATIC = 0
    DYNAMIC = 1

class CollisionNode(PositionNode):
    def __init__(
        self,
        shape: Optional[CollisionShape],
        x: float = 0,
        y: float = 0,
        active_tags: list[str] = [],
        passive_tags: list[str] = [],
        collision_type: CollisionType = CollisionType.STATIC,
        sensor: bool = False,
        color: Optional[tuple[int, int, int, int]] = None,
        on_triggered: Optional[Callable[[list[str], bool], None]] = None
    ) -> None:
        super().__init__(x, y)

        # Velocity components.
        self.velocity_x = 0.0
        self.velocity_y = 0.0

        self.active_tags = active_tags
        self.passive_tags = passive_tags
        self.type = collision_type
        self.sensor = sensor
        self.shape: Optional[CollisionShape] = shape
        self.on_triggered = on_triggered

        self.collisions = set[CollisionNode]()
        self.in_collisions = set[CollisionNode]()
        self.out_collisions = set[CollisionNode]()

        # Set shape color.
        if color is not None:
            self.shape.set_color(color = color)
        else:
            self.shape.set_color(color = SENSOR_COLOR if sensor else COLLIDER_COLOR)

    def delete(self) -> None:
        if self.shape is not None:
            self.shape.delete()
        self.shape = None

    def set_position(
        self,
        position: tuple[float, float],
        z: Optional[float] = None
    ) -> None:
        super().set_position(position)

        if self.shape is not None:
            self.shape.set_position(position = position)

    def get_velocity(self) -> tuple[float, float]:
        return (self.velocity_x, self.velocity_y)

    def put_velocity(
        self,
        velocity: tuple[float, float]
    ) -> None:
        """
        Sums the provided velocity to any already there.
        """
        self.velocity_x += velocity[0]
        self.velocity_y += velocity[1]

        if self.shape is not None:
            self.shape.put_velocity(velocity = velocity)

    def set_velocity(
        self,
        velocity: tuple[float, float]
    ) -> None:
        self.velocity_x = velocity[0]
        self.velocity_y = velocity[1]

        if self.shape is not None:
            self.shape.set_velocity(velocity = velocity)

    def collide(self, other) -> Optional[CollisionHit]:
        assert isinstance(other, CollisionNode)

        # Reset collision time.
        collision_hit = None

        # Make sure there's at least one matching tag.
        if bool(set(self.active_tags) & set(other.passive_tags)):

            # Check collision from shape.
            if self.shape is not None:
                collision_hit = self.shape.swept_collide(other.shape)

            if other not in self.collisions and collision_hit is not None:
                # Store the colliding sensor.
                self.collisions.add(other)
                self.in_collisions.add(other)
            elif other in self.collisions and collision_hit is None:
                # Remove if not colliding anymore.
                self.collisions.remove(other)
                self.out_collisions.add(other)

        return collision_hit