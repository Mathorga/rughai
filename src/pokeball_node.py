from typing import Callable, Optional
import pyglet

from constants import collision_tags
from engine import controllers
from engine.interaction_node import GrabbableNode
from engine.collision.collision_node import CollisionNode, CollisionType
from engine.collision.collision_shape import CollisionCircle

from engine.node import PositionNode
from engine.sprite_node import SpriteNode

class PokeballNode(PositionNode):
    def __init__(
        self,
        x: float = 0,
        y: float = 0,
        on_interaction: Optional[Callable] = None,
        scaling: int = 1,
        batch: Optional[pyglet.graphics.Batch] = None
    ) -> None:
        super().__init__(x, y)

        self.__image = pyglet.resource.image("sprites/pokeball.png")
        self.__image.anchor_x = 2
        self.__image.anchor_y = 2

        self.sprite = SpriteNode(
            resource = self.__image,
            x = x,
            y = y,
            scaling = scaling,
            batch = batch
        )

        self.grab = GrabbableNode(
            on_interaction = on_interaction
        )
        controllers.interaction_controller.add_interaction(self.grab)

        # Interaction finder.
        # This collider is responsible for searching for interactables.
        self.interactor = CollisionNode(
            x = x,
            y = y,
            sensor = True,
            collision_type = CollisionType.STATIC,
            tags = [collision_tags.PLAYER_INTERACTION],
            on_triggered = lambda entered: controllers.interaction_controller.toggle_interaction(self.grab, enable = entered),
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
        controllers.collision_controller.add_collider(self.interactor)

    def update(self, dt: int) -> None:
        self.grab.update(dt)

    def delete(self) -> None:
        self.sprite.delete()
        controllers.interaction_controller.remove_interactor(self.grab)
        self.grab.delete()
        controllers.collision_controller.remove_collider(self.interactor)
        self.interactor.delete()