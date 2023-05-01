from typing import Callable, Optional
import pyglet
from engine.collision.collision_manager import CollisionManager

from engine.collision.collision_node import CollisionNode, CollisionRect
from engine.node import PositionNode

class DoorNode(PositionNode):
    def __init__(
        self,
        collision_manager: CollisionManager,
        x: int = 0,
        y: int = 0,
        width: int = 0,
        height: int = 0,
        anchor_x: int = 0,
        anchor_y: int = 0,
        scaling: int = 1,
        tag: str = "",
        on_triggered: Optional[Callable[[bool], None]] = None,
        batch: Optional[pyglet.graphics.Batch] = None
    ) -> None:
        super().__init__(x, y)

        self.collider = CollisionNode(
            x = x,
            y = y,
            tag = tag,
            sensor = True,
            on_triggered = on_triggered,
            shapes = [
                CollisionRect(
                    x = x,
                    y = y,
                    width = width,
                    height = height,
                    anchor_x = anchor_x,
                    anchor_y = anchor_y,
                    scaling = scaling,
                    batch = batch
                )
            ],
            batch = batch
        )

        collision_manager.add_collider(self.collider)

    def delete(self):
        self.collider.delete()