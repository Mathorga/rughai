import os
from typing import Optional
import pyglet
import pyglet.gl as gl
from constants import collision_tags
from engine.collision.collision_manager import CollisionManager
from engine.collision.collision_node import CollisionNode, CollisionType
from engine.collision.collision_shape import CollisionCircle

from engine.node import PositionNode
from engine.sprite_node import SpriteNode
from engine.utils import *

class PriestNode(PositionNode):
    def __init__(
        self,
        collision_manager: CollisionManager,
        x: float = 0,
        y: float = 0,
        scaling: int = 1,
        batch: Optional[pyglet.graphics.Batch] = None
    ) -> None:
        super().__init__(x, y)

        self.__image = pyglet.resource.image("sprites/rughai/npc/priest_0/priest_0.png")
        self.__image.anchor_x = 4
        self.__image.anchor_y = 0

        self.sprite = SpriteNode(
            resource = self.__image,
            x = x,
            y = y,
            scaling = scaling,
            batch = batch
        )

        # Interaction finder.
        # This collider is responsible for searching for interactables.
        self.interactor = CollisionNode(
            x = x,
            y = y,
            sensor = True,
            collision_type = CollisionType.STATIC,
            tags = [collision_tags.PLAYER_INTERACTION],
            on_triggered = lambda entered: print("SHOW_INTERACTION") if entered else None,
            shapes = [
                CollisionCircle(
                    x = x,
                    y = y,
                    radius = 6,
                    scaling = scaling,
                    batch = batch
                )
            ]
        )
        collision_manager.add_collider(self.interactor)

    def delete(self) -> None:
        self.sprite.delete()
        self.interactor.delete()