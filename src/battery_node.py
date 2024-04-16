import pyglet

from constants import collision_tags
from engine import controllers
from engine.interaction_node import InteractionNode
from engine.collision.collision_node import CollisionNode, CollisionType
from engine.collision.collision_shape import CollisionRect

from engine.sprite_node import SpriteNode
from engine.utils import utils
from props.prop_node import PropNode

class BatteryNode(PropNode):
    __slots__ = (
        "__in_transition",
        "__open_requested",
        "__close_requested",
        "__closed_image",
        "__opened_image",
        "__open_image",
        "__close_image",
        "sprite",
        "interaction",
        "interaction_sensor"
    )

    def __init__(
        self,
        x: float = 0,
        y: float = 0,
        # on_interaction: Optional[Callable] = None,
        world_batch: pyglet.graphics.Batch | None = None,
        ui_batch: pyglet.graphics.Batch | None = None
    ) -> None:
        super().__init__(
            id = "battery",
            x = x,
            y = y,
            world_batch = world_batch,
            ui_batch = ui_batch
        )

        # Opening and closing flag.
        self.__in_transition = False

        self.__open_requested = False
        self.__close_requested = False

        self.__closed_image = pyglet.resource.image("sprites/prop/other/battery/battery_closed.png")
        self.__closed_image.anchor_x = 16
        self.__closed_image.anchor_y = 6

        self.__opened_image = pyglet.resource.image("sprites/prop/other/battery/battery_open.png")
        self.__opened_image.anchor_x = 16
        self.__opened_image.anchor_y = 6

        self.__open_image = pyglet.resource.animation("sprites/prop/other/battery/battery_opening.gif")
        utils.set_animation_anchor(
            animation = self.__open_image,
            x = 16.0,
            y = 6.0
        )

        self.__close_image = pyglet.resource.animation("sprites/prop/other/battery/battery_closing.gif")
        utils.set_animation_anchor(
            animation = self.__close_image,
            x = 16.0,
            y = 6.0
        )

        self.sprite = SpriteNode(
            resource = self.__closed_image,
            x = x,
            y = y,
            batch = world_batch
        )
        self.add_component(component = self.sprite)

        self.interaction = InteractionNode(
            on_toggle = self.__toggle,
            # on_interaction = on_interaction
        )
        controllers.INTERACTION_CONTROLLER.add_interaction(self.interaction)

        # Interaction sensor.
        # This collider is responsible for searching for interactions.
        self.interaction_sensor = CollisionNode(
            x = x,
            y = y,
            sensor = True,
            collision_type = CollisionType.STATIC,
            passive_tags = [collision_tags.PLAYER_INTERACTION],
            on_triggered = lambda tags, entered: controllers.INTERACTION_CONTROLLER.toggle(self.interaction, enable = entered),
            shape = CollisionRect(
                x = x,
                y = y,
                width = 16,
                height = 8,
                anchor_x = 8,
                anchor_y = 4,
                batch = world_batch
            )
        )
        controllers.COLLISION_CONTROLLER.add_collider(self.interaction_sensor)

    def __on_animation_end(self) -> None:
        sprite_image = self.sprite.get_image()
        if self.__open_requested and sprite_image != self.__open_image and sprite_image != self.__opened_image:
            self.sprite.set_image(self.__open_image)
        elif self.__close_requested and sprite_image != self.__close_image and sprite_image != self.__closed_image:
            self.sprite.set_image(self.__close_image)
        else:
            if sprite_image == self.__open_image:
                self.sprite.set_image(self.__opened_image)
            elif sprite_image == self.__close_image:
                self.sprite.set_image(self.__closed_image)

        self.__in_transition = False

    def __toggle(self, enable: bool) -> None:
        self.__open_requested = enable
        self.__close_requested = not enable
        
        if not self.__in_transition:
            self.__in_transition = True
            self.sprite.set_image(self.__open_image if enable else self.__close_image)

    def update(self, dt: int) -> None:
        super().update(dt = dt)

        self.interaction.update(dt)

        if self.sprite.get_frame_index() >= self.sprite.get_frames_num() - 1:
            self.__on_animation_end()

    def delete(self) -> None:
        self.interaction.delete()
        self.interaction_sensor.delete()
        super().delete()