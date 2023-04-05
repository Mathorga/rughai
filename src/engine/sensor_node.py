from types import FunctionType
from typing import Callable, Optional
from engine.node import PositionNode
from engine.rect_node import RectNode
import engine.utils as utils

class SensorNode(PositionNode):
    def __init__(
        self,
        x: int = 0,
        y: int = 0,
        width: int = 0,
        height: int = 0,
        anchor_x: int = 0,
        anchor_y: int = 0,
        scaling: int = 1,
        visible: bool = False,
        batch = None,
        group = None,
        tag: str = "",
        on_triggered: Optional[Callable[[bool], None]] = None
    ) -> None:
        super().__init__(x, y)

        self.width = width
        self.height = height
        self.anchor_x = anchor_x
        self.anchor_y = anchor_y

        self.__scaling = scaling
        self.__visible = visible

        self.tag = tag
        self.__on_triggered = on_triggered

        self.__shape = RectNode(
            x = x,
            y = y,
            width = width,
            height = height,
            scaling = scaling,
            anchor_x = anchor_x,
            anchor_y = anchor_y,
            color = (0xFF, 0xFF, 0x7F, 0x7F),
            batch = batch,
            group = group
        )

        self.collisions = set()

    def delete(self) -> None:
        self.__shape.delete

    def set_position(
        self,
        x = None,
        y = None
    ) -> None:
        if x != None:
            self.x = x

        if y != None:
            self.y = y

        self.__shape.set_position(x, y)

    def draw(self) -> None:
        if self.__visible:
            self.__shape.draw()

    def get_collision_bounds(self):
        return (
            self.__shape.x - self.anchor_x,
            self.__shape.y - self.anchor_y,
            self.width,
            self.height
        )

    def overlap(self, other):
        if (issubclass(type(other), SensorNode) and
            other.tag == self.tag
        ):
            if other not in self.collisions and utils.overlap(
                *self.get_collision_bounds(),
                *other.get_collision_bounds()
            ):
                # Store the colliding sensor.
                self.collisions.add(other)

                # Collision enter callback.
                if self.__on_triggered:
                    self.__on_triggered(True)
            elif other in self.collisions and not utils.overlap(
                *self.get_collision_bounds(),
                *other.get_collision_bounds()
            ):
                # Remove if not colliding anymore.
                self.collisions.remove(other)

                # Collision exit callback.
                if self.__on_triggered:
                    self.__on_triggered(False)