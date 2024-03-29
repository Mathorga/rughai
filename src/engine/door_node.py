from typing import Callable, List, Optional, Tuple
import pyglet

from engine import controllers
from engine.collision.collision_node import CollisionNode
from engine.collision.collision_shape import CollisionRect
from engine.node import PositionNode

DOOR_COLOR: Tuple[int, int, int, int] = (0xFF, 0xFF, 0x7F, 0x7F)

class DoorNode(PositionNode):
    def __init__(
        self,
        x: float = 0,
        y: float = 0,
        width: int = 0,
        height: int = 0,
        anchor_x: float = 0,
        anchor_y: float = 0,
        tags: List[str] = [],
        on_triggered: Optional[Callable[[List[str], bool], None]] = None,
        batch: Optional[pyglet.graphics.Batch] = None
    ) -> None:
        super().__init__(x, y)

        self.collider = CollisionNode(
            x = x,
            y = y,
            passive_tags = tags,
            sensor = True,
            on_triggered = on_triggered,
            color = DOOR_COLOR,
            shape = CollisionRect(
                x = x,
                y = y,
                width = width,
                height = height,
                anchor_x = anchor_x,
                anchor_y = anchor_y,
                batch = batch
            )
        )

        controllers.COLLISION_CONTROLLER.add_collider(self.collider)

    def delete(self):
        self.collider.delete()