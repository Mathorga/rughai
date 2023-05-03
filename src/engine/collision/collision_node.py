from enum import Enum
from types import FunctionType
from typing import Callable, List, Optional, Tuple
import pyglet
import pyglet.math as pm

from engine.collision.collision_shape import CollisionShape
from engine.node import PositionNode
from engine.rect_node import RectNode
import engine.utils as utils

class CollisionType(Enum):
    STATIC = 0
    DYNAMIC = 1

class CollisionNode(PositionNode):
    def __init__(
        self,
        x: float = 0,
        y: float = 0,
        tag: str = "",
        type: CollisionType = CollisionType.STATIC,
        sensor: bool = False,
        shapes: List[CollisionShape] = [],
        on_triggered: Optional[Callable[[bool], None]] = None
    ) -> None:
        super().__init__(x, y)

        self.tag = tag
        self.type = type
        self.sensor = sensor
        self.shapes: List[CollisionShape] = shapes
        self.on_triggered = on_triggered

        self.collisions = set()

    def delete(self) -> None:
        for shape in self.shapes:
            shape.delete()

    def set_position(
        self,
        position: Tuple[float, float]
    ) -> None:
        self.x = position[0]
        self.y = position[1]

        for shape in self.shapes:
            shape.set_position(position)

    def collide(self, other) -> None:
        assert isinstance(other, CollisionNode)

        collision: Tuple[float, float] = (0.0, 0.0)
        collisions: List[pm.Vec2] = []

        if other.tag == self.tag:
            overlap: bool = False
            for shape in self.shapes:
                for other_shape in other.shapes:
                    overlap = shape.overlap(other_shape)
                    if overlap:
                        collision = shape.collide(other_shape)
                        collisions.append(pm.Vec2(*collision))
                #         break
                # else:
                #     continue
                # break

            if not other.sensor:
                self.set_position((self.x + collision[0], self.y + collision[1]))

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