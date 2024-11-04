import math
from typing import Callable
import pyglet
import pyglet.math as pm

from amonite.loading_indicator_node import LoadingIndicatorNode
from amonite.utils import utils
from amonite.utils.tween import Tween
import amonite.controllers as controllers
from amonite.animation import Animation
from amonite.collision.collision_node import CollisionNode
from amonite.collision.collision_node import CollisionType
from amonite.collision.collision_shape import CollisionRect
from amonite.node import PositionNode
from amonite.sprite_node import SpriteNode
from amonite.settings import GLOBALS
from amonite.settings import SETTINGS
from amonite.settings import Keys

from player_stats import PlayerStats
from scope_node import ScopeNode
from constants import collision_tags

class IryoDataNode(PositionNode):
    __slots__ = (
        "batch",
        "run_threshold",
        "stats",
        "__hor_facing",
        "__shoot_mag",
        "draw_time",
        "draw_sound",
        "shoot_sound",
        "__sprite",

        "scope_offset",
        "__scope",
        "draw_indicator",
        "interactor_distance",
        "__shadow_sprite",
        "__collider",
        "__interactor",

        # Cam target info.
        "__cam_target_distance",
        "__cam_target_distance_fill",
        "__cam_target_offset",
        "__cam_target",
    )

    def __init__(
        self,
        cam_target: PositionNode,
        cam_target_offset: tuple = (0.0, 8.0),
        x: float = 0,
        y: float = 0,
        on_sprite_animation_end: Callable | None = None,
        on_collision: Callable | None = None,
        batch: pyglet.graphics.Batch | None = None
    ) -> None:
        PositionNode.__init__(
            self,
            x = x,
            y = y
        )

        self.batch: pyglet.graphics.Batch | None = batch

        self.interactor_distance: float = 5.0

        self.run_threshold: float = 0.75

        self.stats: PlayerStats = PlayerStats(
            vitality = 5,
            resistance = 5,
            odds = 5,
            variation = 0.2
        )

        self.__hor_facing: int = 1

        # Current draw time (in seconds).
        self.draw_time: float = 0.0

        # Draw sound.
        self.draw_sound: pyglet.media.StaticSource = pyglet.media.StaticSource(pyglet.resource.media(name = "sounds/iryo_draw_1.wav"))
        self.shoot_sound: pyglet.media.StaticSource = pyglet.media.StaticSource(pyglet.resource.media(name = "sounds/iryo_shoot_1.wav"))

        # Animations.
        self.__sprite = SpriteNode(
            resource = Animation(source = "sprites/iryo/iryo_idle.json").content,
            on_animation_end = on_sprite_animation_end,
            x = x,
            y = y,
            batch = batch
        )

        # Scope.
        self.scope_offset: tuple[float, float] = (0.0, 8.0)
        self.__scope = ScopeNode(
            x = self.x,
            y = self.y,
            offset_x = self.scope_offset[0],
            offset_y = self.scope_offset[1],
            batch = batch
        )

        # Draw loading indicator.
        self.draw_indicator: LoadingIndicatorNode = LoadingIndicatorNode(
            foreground_sprite_res = pyglet.resource.image("sprites/loading_foreground.png"),
            background_sprite_res = pyglet.resource.image("sprites/loading_background.png"),
            x = self.x,
            y = self.y,
            offset_y = 4,
            ease_function = Tween.cubeInOut,
            batch = batch
        )

        # Shadow sprite image.
        shadow_image = pyglet.resource.image("sprites/shadow.png")
        utils.set_anchor(shadow_image, center = True)

        self.__shadow_sprite = SpriteNode(
            resource = shadow_image,
            x = x,
            y = y,
            y_sort = False,
            batch = batch
        )

        # Collider.
        self.__collider = CollisionNode(
            x = x,
            y = y,
            collision_type = CollisionType.DYNAMIC,
            active_tags = [
                collision_tags.PLAYER_COLLISION,
                collision_tags.PLAYER_SENSE,
                collision_tags.FALL
            ],
            passive_tags = [
                collision_tags.DAMAGE
            ],
            shape = CollisionRect(
                x = x,
                y = y,
                anchor_x = 3,
                anchor_y = 3,
                width = 6,
                height = 6,
                batch = batch
            ),
            on_triggered = on_collision
        )
        controllers.COLLISION_CONTROLLER.add_collider(self.__collider)

        # Interaction finder.
        # This collider is responsible for searching for interactables.
        self.__interactor = CollisionNode(
            x = x,
            y = y,
            sensor = True,
            collision_type = CollisionType.DYNAMIC,
            active_tags = [collision_tags.PLAYER_INTERACTION],
            shape = CollisionRect(
                x = x,
                y = y,
                anchor_x = 4,
                anchor_y = 4,
                width = 8,
                height = 8,
                batch = batch
            )
        )
        controllers.COLLISION_CONTROLLER.add_collider(self.__interactor)

        self.__cam_target_distance = 50.0
        self.__cam_target_distance_fill = 0.0
        self.__cam_target_offset = cam_target_offset
        self.__cam_target = cam_target
        self.__cam_target.x = x + cam_target_offset[0]
        self.__cam_target.y = y + cam_target_offset[1]

    def delete(self) -> None:
        self.__sprite.delete()
        self.__shadow_sprite.delete()
        self.__collider.delete()
        self.__interactor.delete()
        self.__scope.delete()
        self.draw_indicator.delete()

    def update(self, dt) -> None:
        super().update(dt = dt)

        # Update sprites accordingly.
        self.__update_sprites(dt = dt)

    def set_position(
        self,
        position: tuple[float, float],
        z: float | None = None
    ):
        super().set_position(position = position, z = z)
        self.__collider.set_position(position = position)

    def get_input_movement(self) -> bool:
        return controllers.INPUT_CONTROLLER.get_movement()

    def get_input_aim(self) -> bool:
        return False if controllers.INVENTORY_CONTROLLER.is_open or controllers.MENU_CONTROLLER.is_open else controllers.INPUT_CONTROLLER.get_aim()

    def get_input_movement_vec(self) -> pm.Vec2:
        return controllers.INPUT_CONTROLLER.get_movement_vec()

    def get_input_aim_vec(self) -> pm.Vec2:
        return pm.Vec2() if controllers.INVENTORY_CONTROLLER.is_open or controllers.MENU_CONTROLLER.is_open else controllers.INPUT_CONTROLLER.get_aim_vec()

    def get_input_sprint(self) -> bool:
        return controllers.INPUT_CONTROLLER.get_sprint()

    def get_input_shift(self) -> bool:
        return controllers.INPUT_CONTROLLER.get_shift()

    def get_input_interaction(self) -> bool:
        return controllers.INPUT_CONTROLLER.get_interaction()

    def get_input_draw(self) -> bool:
        return controllers.INPUT_CONTROLLER.get_draw()

    def set_animation(self, animation: Animation) -> None:
        self.__sprite.set_image(animation.content)

    def __set_velocity(self, velocity: pyglet.math.Vec2) -> None:
        # Apply the computed velocity to all colliders.
        self.__collider.set_velocity((
            round(velocity.x, GLOBALS[Keys.FLOAT_ROUNDING]),
            round(velocity.y, GLOBALS[Keys.FLOAT_ROUNDING])
        ))
        self.__interactor.set_velocity((
            round(velocity.x, GLOBALS[Keys.FLOAT_ROUNDING]),
            round(velocity.y, GLOBALS[Keys.FLOAT_ROUNDING])
        ))

    def move(self, dt: float) -> None:
        # Apply movement after collision.
        self.set_position(self.__collider.get_position())

        # Compute velocity.
        velocity: pyglet.math.Vec2 = pm.Vec2.from_polar(self.stats.speed, self.stats.move_dir)

        self.__set_velocity(velocity = velocity)

    def __update_sprites(self, dt):
        # Only update facing if there's any horizontal movement.
        dir_cos = math.cos(self.stats.look_dir)
        dir_len = abs(dir_cos)
        if dir_len > 0.1:
            self.__hor_facing = int(math.copysign(1.0, dir_cos))

        # Update sprite position.
        self.__sprite.set_position(self.get_position())

        # Flip sprite if moving to the left.
        self.__sprite.set_scale(x_scale = self.__hor_facing)

        # Update scope.
        self.__update_scope(dt)

        # Update shadow sprite.
        self.__update_shadow(dt)

        self.__update_draw_indicator(dt)

        # Update camera target.
        self.__update_cam_target(dt)

        # Update interactor.
        self.__update_interactor(dt)

    def __update_scope(self, dt):
        """
        Updates the scope sign.
        """

        self.__scope.set_direction(direction = self.stats.look_dir)
        self.__scope.set_position(position = self.get_position())
        self.__scope.update(dt = dt)

    def __update_shadow(self, dt):
        self.__shadow_sprite.set_position(
            position = self.get_position(),
            # z = 0
            z = -(self.y + (SETTINGS[Keys.LAYERS_Z_SPACING] * 0.1))
        )
        self.__shadow_sprite.update(dt)

    def __update_draw_indicator(self, dt):
        """
        Updates the draw indicator.
        """

        draw_indicator_value: float = pm.clamp(
            num = self.draw_time,
            min_val = 0.0,
            max_val = self.stats.min_draw_time
        )
        self.draw_indicator.set_fill(fill = draw_indicator_value / self.stats.min_draw_time)
        self.draw_indicator.set_position(position = self.get_position())
        self.draw_indicator.update(dt = dt)

    def set_cam_target_distance_fill(self, fill: float) -> None:
        """
        Sets the fill (between 0 and 1) for cam target distance.
        """

        assert fill >= 0.0 and fill <= 1.0, "Value out of range"

        self.__cam_target_distance_fill = fill

    def __update_cam_target(self, dt: float):
        # Automatically go to cam target distance if loading or aiming.
        cam_target_distance: float = self.__cam_target_distance * self.__cam_target_distance_fill

        cam_target_vec: pyglet.math.Vec2 = pyglet.math.Vec2.from_polar(cam_target_distance, self.stats.look_dir)
        self.__cam_target.x = self.x + self.__cam_target_offset[0] + cam_target_vec.x
        self.__cam_target.y = self.y + self.__cam_target_offset[1] + cam_target_vec.y
        self.__cam_target.update(dt)

    # def set_cam_target_position(self, )

    def __update_interactor(self, dt):
        aim_vec = pyglet.math.Vec2.from_polar(self.interactor_distance, self.stats.look_dir)
        self.__interactor.set_position(
            position = (
                self.x + aim_vec.x,
                self.y + aim_vec.y
            ),
        )

        self.__interactor.update(dt)

    def load_scope(self) -> None:
        self.__scope.load()

    def unload_scope(self) -> None:
        self.__scope.unload()

    def __update_collider(self, dt):
        self.__collider.update(dt)

    def get_bounding_box(self):
        return self.__sprite.get_bounding_box()