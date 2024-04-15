from typing import Optional
import pyglet

from constants import collision_tags
from engine.dialog_node import DialogNode
from engine.node import PositionNode
from engine.sprite_node import SpriteNode
from props.prop_node import PropNode

class StanLeeNode(PropNode):
    def __init__(
        self,
        x: float = 0,
        y: float = 0,
        world_batch: Optional[pyglet.graphics.Batch] = None,
        ui_batch: Optional[pyglet.graphics.Batch] = None,
    ) -> None:
        super().__init__(
            id = "stan_lee",
            x = x,
            y = y,
            world_batch = world_batch,
            ui_batch = ui_batch
        )

        self.__image = pyglet.resource.image("sprites/prop/other/stan_lee/stan_lee.png")
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
                "Welcome true believers and newcomers alike!",
                "Spiderman co-creator Stan Lee here!",
                "Once again we find our hero Peter Parker,",
                "better known around the world as the amazing Spider-Man...",
                "...in a heap of trouble!",
                "But this is just the beginning, Spidey fans.",
                "So get ready for a true superhero action thriller,",
                "packed to the brim with thrills and chills,",
                "twists and turns,",
                "more super-villains than you can shake a web at",
                "and of course, non-stop web-slinging, wall-crawling action!"
            ],
            tags = [collision_tags.PLAYER_INTERACTION],
            world_batch = world_batch,
            ui_batch = ui_batch
        )

    def set_position(
        self,
        position: tuple[float, float],
        z: float | None = None
    ):
        super().set_position(position = position, z = z)

        # Update sprite position as well.
        self.sprite.set_position(position = position, z = z)

    def update(self, dt: int) -> None:
        super().update(dt = dt)
        self.dialog.update(dt)

    def delete(self) -> None:
        self.sprite.delete()
        self.dialog.delete()