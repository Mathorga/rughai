from enum import Enum
from typing import Callable, List, Optional, Tuple
import pyglet.math as pm

from engine.collision.collision_shape import CollisionShape
from engine.node import PositionNode
from engine.utils import CollisionHit

class CollisionType(Enum):
    STATIC = 0
    DYNAMIC = 1

class CollisionNode(PositionNode):
    def __init__(
        self,
        x: float = 0,
        y: float = 0,
        active_tags: List[str] = [],
        passive_tags: List[str] = [],
        collision_type: CollisionType = CollisionType.STATIC,
        sensor: bool = False,
        shapes: List[CollisionShape] = [],
        on_triggered: Optional[Callable[[List[str], bool], None]] = None
    ) -> None:
        super().__init__(x, y)

        # Velocity components.
        self.velocity_x = 0.0
        self.velocity_y = 0.0

        self.active_tags = active_tags
        self.passive_tags = passive_tags
        self.type = collision_type
        self.sensor = sensor
        self.shapes: List[CollisionShape] = shapes
        self.on_triggered = on_triggered

        self.collisions = set()

    def delete(self) -> None:
        for shape in self.shapes:
            shape.delete()

    def set_position(
        self,
        position: Tuple[float, float],
        z: Optional[float] = None
    ) -> None:
        super().set_position(position)

        for shape in self.shapes:
            shape.set_position(position)

    def get_velocity(self) -> Tuple[float, float]:
        return (self.velocity_x, self.velocity_y)

    def put_velocity(
        self,
        velocity: Tuple[float, float]
    ) -> None:
        """
        Sums the provided velocity to any already there.
        """
        self.velocity_x += velocity[0]
        self.velocity_y += velocity[1]

        for shape in self.shapes:
            shape.put_velocity(velocity)

    def set_velocity(
        self,
        velocity: Tuple[float, float]
    ) -> None:
        self.velocity_x = velocity[0]
        self.velocity_y = velocity[1]

        for shape in self.shapes:
            shape.set_velocity(velocity)

    def collide(self, other) -> Optional[CollisionHit]:
        assert isinstance(other, CollisionNode)

        # Reset collision time.
        collision_hit = None

        # Make sure there's at least one matching tag.
        if bool(set(self.active_tags) & set(other.passive_tags)):

            # Only consider the first shape for now.
            # TODO Use all shapes.
            if len(self.shapes) > 0:
                collision_hit = self.shapes[0].swept_collide(other.shapes[0])

            if other not in self.collisions and collision_hit is not None:
                # Store the colliding sensor.
                self.collisions.add(other)
                other.collisions.add(self)

                # Collision enter callback.
                if self.on_triggered is not None:
                    self.on_triggered(other.passive_tags, True)
                if other.on_triggered is not None:
                    other.on_triggered(self.active_tags, True)
            elif other in self.collisions and collision_hit is None:
                # Remove if not colliding anymore.
                self.collisions.remove(other)
                other.collisions.remove(self)

                # Collision exit callback.
                if self.on_triggered is not None:
                    self.on_triggered(other.active_tags, False)
                if other.on_triggered is not None:
                    other.on_triggered(self.active_tags, False)

        return collision_hit