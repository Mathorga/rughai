from enum import Enum
from typing import Callable, List, Optional, Tuple
import pyglet.math as pm

from engine.collision.collision_shape import CollisionShape
from engine.node import PositionNode

class CollisionType(Enum):
    STATIC = 0
    DYNAMIC = 1

class CollisionNode(PositionNode):
    def __init__(
        self,
        x: float = 0,
        y: float = 0,
        tags: List[str] = [],
        collision_type: CollisionType = CollisionType.STATIC,
        sensor: bool = False,
        shapes: List[CollisionShape] = [],
        on_triggered: Optional[Callable[[bool], None]] = None
    ) -> None:
        super().__init__(x, y)

        # Velocity components.
        self.velocity_x = 0.0
        self.velocity_y = 0.0

        self.tags = tags
        self.type = collision_type
        self.sensor = sensor
        self.shapes: List[CollisionShape] = shapes
        self.on_triggered = on_triggered

        self.collisions = set()

        # A collision time >= 1.0 means no collision at all.
        self.collision_time = 1.0

    def delete(self) -> None:
        for shape in self.shapes:
            shape.delete()

    def set_position(
        self,
        position: Tuple[float, float],
        z: Optional[float] = None
    ) -> None:
        self.x = position[0]
        self.y = position[1]

        for shape in self.shapes:
            shape.set_position(position)

    def set_velocity(
        self,
        velocity: Tuple[float, float]
    ) -> None:
        self.velocity_x = velocity[0]
        self.velocity_y = velocity[1]

        for shape in self.shapes:
            shape.set_velocity(velocity)

    def update(self, dt: int) -> None:
        self.set_position((self.x + self.velocity_x * self.collision_time, self.y + self.velocity_y * self.collision_time))

        # Reset collision time.
        self.collision_time = 1.0

    def collide(self, other) -> None:
        assert isinstance(other, CollisionNode)

        collision: Tuple[float, float] = (0.0, 0.0)
        collisions: List[pm.Vec2] = []

        # Reset collision time.
        collision_time = 1.0
        normal_x = 0.0
        normal_y = 0.0

        # Make sure there's at least one matching tag.
        if bool(set(self.tags) & set(other.tags)):
            overlap: bool = False
            for shape in self.shapes:
                for other_shape in other.shapes:
                    collision_time, normal_x, normal_y = shape.swept_collide(other_shape)
                    if collision_time < 1.0:
                        collisions.append(pm.Vec2(normal_x, normal_y))

                    # overlap = shape.overlap(other_shape)
                    # if overlap:
                    #     collision = shape.collide(other_shape)
                    #     collisions.append(pm.Vec2(*collision))

            if not other.sensor:
                # Overwrite collision time if a smaller one is found.
                if collision_time < self.collision_time:
                    self.collision_time = collision_time

                # self.set_position((self.x + collision[0], self.y + collision[1]))

            if other not in self.collisions and overlap:
                # Store the colliding sensor.
                self.collisions.add(other)
                other.collisions.add(self)

                # Collision enter callback.
                if self.on_triggered is not None:
                    self.on_triggered(True)
                if other.on_triggered is not None:
                    other.on_triggered(True)
            elif other in self.collisions and not overlap:
                # Remove if not colliding anymore.
                self.collisions.remove(other)
                other.collisions.remove(self)

                # Collision exit callback.
                if self.on_triggered is not None:
                    self.on_triggered(False)
                if other.on_triggered is not None:
                    other.on_triggered(False)