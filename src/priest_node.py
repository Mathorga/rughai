from typing import Optional
import pyglet
from constants import collision_tags

from engine.dialog_node import DialogNode
from engine.node import PositionNode
from engine.sprite_node import SpriteNode

class PriestNode(PositionNode):
    def __init__(
        self,
        x: float = 0,
        y: float = 0,
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
            batch = world_batch
        )

        self.dialog = DialogNode(
            x = self.x,
            y = self.y,
            lines = [
                "Welcome true believers and newcomers alike! Spiderman co-creator Stan Lee here!",
                "How's it gonna be today?",
                "Oh I see! You're gonna make a mess as usual",
                "Just be careful with those pokemon over there, I'd like to eat them eventually."
            ],
            tags = [collision_tags.PLAYER_INTERACTION],
            world_batch = world_batch,
            ui_batch = ui_batch
        )

    def update(self, dt: int) -> None:
        self.dialog.update(dt)

    def delete(self) -> None:
        self.sprite.delete()
        self.dialog.delete()