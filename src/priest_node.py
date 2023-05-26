from typing import Optional
import pyglet

from constants import collision_tags
from engine.settings import settings, Builtins
from engine.collision.collision_manager import CollisionManager
from engine.collision.collision_node import CollisionNode, CollisionType
from engine.collision.collision_shape import CollisionCircle

from engine.node import PositionNode
from engine.sprite_node import SpriteNode
from engine.text_node import TextNode

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

        self.off_text = ""
        self.on_text = "Goodbye, cruel world."
        self.current_text_length = 0
        self.interacting = False

        self.dialog = TextNode(
            text = self.off_text,
            font_name = settings[Builtins.FONT_NAME],
            x = settings[Builtins.VIEW_WIDTH] / 2,
            y = 16,
            scaling = scaling,
            font_size = 6,
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
            on_triggered = self.on_interaction,
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

    def on_interaction(self, entered: bool):
        self.interacting = entered

    def update(self, dt: int) -> None:
        if self.interacting:
            self.current_text_length += 1
            if self.current_text_length >= len(self.on_text):
                self.current_text_length = len(self.on_text)
        else:
            self.current_text_length = 0

        self.dialog.set_text(self.on_text[0:self.current_text_length])

    def delete(self) -> None:
        self.sprite.delete()
        self.interactor.delete()
        self.dialog.delete()