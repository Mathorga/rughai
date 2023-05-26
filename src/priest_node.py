from typing import Optional
import pyglet

from constants import collision_tags
from engine.dialog_node import DialogNode
from engine.settings import settings, Builtins
from engine.collision.collision_manager import CollisionManager
from engine.collision.collision_node import CollisionNode, CollisionType
from engine.collision.collision_shape import CollisionCircle

from engine.node import PositionNode
from engine.sprite_node import SpriteNode

class PriestNode(PositionNode):
    def __init__(
        self,
        collision_manager: CollisionManager,
        x: float = 0,
        y: float = 0,
        scaling: int = 1,
        world_batch: Optional[pyglet.graphics.Batch] = None,
        ui_batch: Optional[pyglet.graphics.Batch] = None,
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
            batch = world_batch
        )

        self.dialog = DialogNode(
            x = settings[Builtins.VIEW_WIDTH] / 2,
            y = 16,
            scaling = scaling,
            batch = ui_batch
        )

        # Interaction finder.
        # This collider is responsible for searching for interactables.
        self.interactor = CollisionNode(
            x = x,
            y = y,
            sensor = True,
            collision_type = CollisionType.STATIC,
            tags = [collision_tags.PLAYER_INTERACTION],
            on_triggered = lambda entered: self.dialog.enable(entered),
            shapes = [
                CollisionCircle(
                    x = x,
                    y = y,
                    radius = 8,
                    scaling = scaling,
                    batch = world_batch
                )
            ]
        )
        collision_manager.add_collider(self.interactor)

    def update(self, dt: int) -> None:
        self.dialog.update(dt)

    def delete(self) -> None:
        self.sprite.delete()
        self.interactor.delete()
        self.dialog.delete()