from typing import Optional
import pyglet

from constants import collision_tags
from engine import controllers
from engine.interaction_node import DialogNode
from engine.collision.collision_node import CollisionNode, CollisionType
from engine.collision.collision_shape import CollisionCircle

from engine.node import PositionNode
from engine.sprite_node import SpriteNode

class PriestNode(PositionNode):
    def __init__(
        self,
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
            lines = [
                "Welcome true believers and newcomers alike! Spiderman co-creator Stan Lee here!",
                "How's it gonna be today?",
                "Oh I see! You're gonna make a mess as usual",
                "Just be careful with those pokemon over there, I'd like to eat them eventually."
            ],
            scaling = scaling,
            batch = ui_batch
        )
        controllers.interaction_controller.add_interaction(self.dialog)

        # Interaction finder.
        # This collider is responsible for searching for interactables.
        self.interactor = CollisionNode(
            x = x,
            y = y,
            sensor = True,
            collision_type = CollisionType.STATIC,
            tags = [collision_tags.PLAYER_INTERACTION],
            on_triggered = lambda entered: controllers.interaction_controller.toggle_interaction(self.dialog, enable = entered),
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
        controllers.collision_controller.add_collider(self.interactor)

    def update(self, dt: int) -> None:
        self.dialog.update(dt)

    def delete(self) -> None:
        self.sprite.delete()
        self.interactor.delete()
        self.dialog.delete()