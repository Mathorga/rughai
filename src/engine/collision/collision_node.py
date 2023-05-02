from enum import Enum
from types import FunctionType
from typing import Callable, List, Optional, Tuple
import pyglet

from engine.node import PositionNode
from engine.rect_node import RectNode
import engine.utils as utils

class CollisionType(Enum):
    STATIC = 0
    DYNAMIC = 1

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

    def set_velocity(
        self,
        velocity: Tuple[float, float]
    ) -> None:
        pass

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

        self.velocity = (0.0, 0.0)
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

    def set_velocity(
        self,
        velocity: Tuple[float, float]
    ) -> None:
        self.velocity = velocity

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
            return utils.rect_rect_collision(
                *self.get_collision_bounds(),
                *other.get_collision_bounds()
            )
        else:
            # Other.
            return False

    def collide(self, other) -> Tuple[float, float]:
        if isinstance(other, CollisionRect):
            # Rect/rect collision.
            return utils.resolve_collision(
                *self.get_collision_bounds(),
                *other.get_collision_bounds()
            )
        else:
            # Other.
            return (0, 0)

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

        self.velocity = (0.0, 0.0)
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

    def set_velocity(
        self,
        velocity: Tuple[float, float]
    ) -> None:
        self.velocity = velocity

        for shape in self.shapes:
            shape.set_velocity(velocity)

    def collide(self, other) -> None:
        assert isinstance(other, CollisionNode)

        collision: Tuple[float, float] = (0.0, 0.0)

        if other.tag == self.tag:
            overlap: bool = False
            for shape in self.shapes:
                for other_shape in other.shapes:
                    overlap = shape.overlap(other_shape)
                    if overlap:
                        collision = shape.collide(other_shape)
                        break
                else:
                    continue
                break

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