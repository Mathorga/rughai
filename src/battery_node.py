from typing import Callable, Optional
import pyglet

from constants import collision_tags
from engine import controllers, utils
from engine.interaction_node import InteractionNode
from engine.collision.collision_node import CollisionNode, CollisionType
from engine.collision.collision_shape import CollisionRect

from engine.node import PositionNode
from engine.sprite_node import SpriteNode

class BatteryNode(PositionNode):
    def __init__(
        self,
        x: float = 0,
        y: float = 0,
        on_interaction: Optional[Callable] = None,
        batch: Optional[pyglet.graphics.Batch] = None
    ) -> None:
        super().__init__(x, y)

        self.__closed_image = pyglet.resource.image("sprites/battery/battery_closed.png")
        self.__closed_image.anchor_x = 16
        self.__closed_image.anchor_y = 6

        self.__opened_image = pyglet.resource.image("sprites/battery/battery_opened.png")
        self.__opened_image.anchor_x = 16
        self.__opened_image.anchor_y = 6

        self.__open_image = pyglet.resource.animation("sprites/battery/battery_open.gif")
        utils.animation_set_anchor(
            animation = self.__open_image,
            x = 16.0,
            y = 6.0
        )

        self.__close_image = pyglet.resource.animation("sprites/battery/battery_close.gif")
        utils.animation_set_anchor(
            animation = self.__close_image,
            x = 16.0,
            y = 6.0
        )

        self.sprite = SpriteNode(
            resource = self.__closed_image,
            x = x,
            y = y,
            batch = batch
        )

        self.interaction = InteractionNode(
            on_toggle = self.__toggle,
            on_interaction = on_interaction
        )
        controllers.INTERACTION_CONTROLLER.add_interaction(self.interaction)

        # Interaction sensor.
        # This collider is responsible for searching for interactions.
        self.interaction_sensor = CollisionNode(
            x = x,
            y = y,
            sensor = True,
            collision_type = CollisionType.STATIC,
            tags = [collision_tags.PLAYER_INTERACTION],
            on_triggered = lambda entered: controllers.INTERACTION_CONTROLLER.toggle(self.interaction, enable = entered),
            shapes = [
                CollisionRect(
                    x = x,
                    y = y,
                    width = 16,
                    height = 8,
                    anchor_x = 8,
                    anchor_y = 4,
                    batch = batch
                )
            ]
        )
        controllers.COLLISION_CONTROLLER.add_collider(self.interaction_sensor)

    def __on_animation_end(self) -> None:
        sprite_image = self.sprite.get_image()
        if sprite_image == self.__open_image:
            self.sprite.set_image(self.__opened_image)
        elif sprite_image == self.__close_image:
            self.sprite.set_image(self.__closed_image)

    def __toggle(self, enable: bool) -> None:
        self.sprite.set_image(self.__open_image if enable else self.__close_image)

    def update(self, dt: int) -> None:
        self.interaction.update(dt)

        if self.sprite.get_frame_index() >= self.sprite.get_frames_num() - 1:
            self.__on_animation_end()

    def delete(self) -> None:
        self.sprite.delete()
        controllers.INTERACTION_CONTROLLER.remove_interactor(self.interaction)
        self.interaction.delete()
        controllers.COLLISION_CONTROLLER.remove_collider(self.interaction_sensor)
        self.interaction_sensor.delete()