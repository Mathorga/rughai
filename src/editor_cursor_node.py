import math
from typing import Optional

import pyglet
import pyglet.math as pm
from pyglet.window import key

from constants import collision_tags

from engine.collision.collision_node import CollisionNode, CollisionType
from engine.collision.collision_shape import CollisionRect
from engine.node import PositionNode
from engine.sprite_node import SpriteNode
from engine.settings import SETTINGS, Builtins
import engine.controllers as controllers

from player_stats import PlayerStats
from player_node import PlayerInput

class EditorCursornode(PositionNode):
    """
    Main player class.
    """

    def __init__(
        self,
        cam_target: PositionNode,
        cam_target_distance: float = 50.0,
        cam_target_offset: tuple = (0.0, 8.0),
        x: float = 0,
        y: float = 0,
        run_threshold: float = 0.75,
        batch: Optional[pyglet.graphics.Batch] = None
    ) -> None:
        PositionNode.__init__(
            self,
            x = x,
            y = y
        )

        # Setup input handling.
        self.__controls_enabled = True
        self.__input = PlayerInput()
        self.__move_input = pyglet.math.Vec2()
        self.__look_input = pyglet.math.Vec2()

        # TODO Replace with lines.
        self.__sprite = SpriteNode(
            resource = self.__idle_anim,
            on_animation_end = self.on_sprite_animation_end,
            x = x,
            y = y,
            batch = batch
        )

        # Collider.
        self.__collider = CollisionNode(
            x = x,
            y = y,
            collision_type = CollisionType.DYNAMIC,
            tags = [collision_tags.PLAYER_COLLISION],
            shapes = [
                # CollisionCircle(
                #     x = x,
                #     y = y,
                #     radius = 4,
                #     batch = batch
                # ),
                CollisionRect(
                    x = x,
                    y = y,
                    anchor_x = 3,
                    anchor_y = 3,
                    width = 6,
                    height = 6,
                    batch = batch
                )
            ]
        )
        controllers.COLLISION_CONTROLLER.add_collider(self.__collider)

        self.__cam_target_distance = cam_target_distance
        self.__cam_target_offset = cam_target_offset
        self.__cam_target = cam_target
        self.__cam_target.x = x + cam_target_offset[0]
        self.__cam_target.y = y + cam_target_offset[1]

    def delete(self) -> None:
        self.__sprite.delete()
        self.__collider.delete()

    def draw(self):
        # Draw collider out of batch.
        self.__collider.draw()

        self.__sprite.draw()

    def update(self, dt) -> None:
        # Fetch input.
        self.__fetch_input()

        # Update stats based on input.
        self.__update_stats(dt)

        # Compute and apply movement to self's x and y coords.
        self.__move(dt)

        # Update collider.
        # self.__update_collider(dt)

        # Update sprites accordingly.
        self.__update_sprites(dt)

    def disable_controls(self):
        """
        Disables user controls over the player and stops all existing inputs.
        """

        self.__look_input = pm.Vec2()
        self.__move_input = pm.Vec2()
        self.__controls_enabled = False

    def __fetch_input(self):
        if self.__controls_enabled:
            # Allow the player to look around even if they're rolling.
            self.__look_input = self.__input.get_look_input().limit(1.0)

            self.__move_input = self.__input.get_move_input().limit(1.0)

            # Trigger dialogs' next line.
            interact = self.__input.get_interaction()
            if interact:
                controllers.INTERACTION_CONTROLLER.interact()

    def __move(self, dt):
        # Apply movement after collision.
        self.set_position(self.__collider.get_position())

        # Compute velocity.
        velocity = self.__compute_velocity(dt)

        # Apply the computed velocity to all colliders.
        self.__collider.set_velocity((round(velocity.x, 5), round(velocity.y, 5)))
        self.__interactor.set_velocity((round(velocity.x, 5), round(velocity.y, 5)))

    def __update_sprites(self, dt):
        # Only update facing if there's any horizontal movement.
        dir_cos = math.cos(self.__stats.dir)
        dir_len = abs(dir_cos)
        if dir_len > 0.1:
            self.__hor_facing = int(math.copysign(1.0, dir_cos))

        # Update sprite position.
        self.__sprite.set_position((self.x, self.y))

        # Flip sprite if moving to the left.
        self.__sprite.set_scale(x_scale = self.__hor_facing)

        # Update sprite image based on current speed.
        image_to_show = None
        if self.__sprint_ing:
            image_to_show = self.__sprint_anim
        elif self.__main_atk_ing:
            image_to_show = self.__atk_0_anim
        else:
            if self.__stats.speed <= 0:
                image_to_show = self.__idle_anim
            elif self.__stats.speed < self.__stats.max_speed * self.__run_threshold:
                image_to_show = self.__walk_anim
            else:
                image_to_show = self.__run_anim
        
        # if image_to_show != None and self.__sprite.get_image() != image_to_show:
        self.__sprite.set_image(image_to_show)
        self.__sprite.update(dt = dt)

        # Update aim sprite.
        self.__update_aim(dt)

        # Update shadow sprite.
        self.__update_shadow(dt)

        # Update camera target.
        self.__update_cam_target(dt)

        # Update interactor.
        self.__update_interactor(dt)

    def __update_aim(self, dt):
        aim_vec = pyglet.math.Vec2.from_polar(self.__aim_sprite_distance, self.__stats.dir)
        self.__aim_sprite.set_position(
            position = (
                self.x + self.__aim_sprite_offset[0] + aim_vec.x,
                self.y + self.__aim_sprite_offset[1] + aim_vec.y
            ),
            z = self.y + SETTINGS[Builtins.LAYERS_Z_SPACING] * 0.5
        )
        self.__aim_sprite.update(dt)

    def __update_shadow(self, dt):
        self.__shadow_sprite.set_position(
            position = (self.x, self.y),
            # z = 0
            z = -(self.y + (SETTINGS[Builtins.LAYERS_Z_SPACING] * 0.5))
        )
        self.__shadow_sprite.update(dt)

    def __update_cam_target(self, dt):
        cam_target_vec = pyglet.math.Vec2.from_polar(self.__cam_target_distance * self.__look_input.mag, self.__look_input.heading)
        self.__cam_target.x = self.x + self.__cam_target_offset[0] + cam_target_vec.x
        self.__cam_target.y = self.y + self.__cam_target_offset[1] + cam_target_vec.y
        self.__cam_target.update(dt)

    def __update_interactor(self, dt):
        aim_vec = pyglet.math.Vec2.from_polar(self.__interactor_distance, self.__stats.dir)
        self.__interactor.set_position(
            position = (
                self.x + aim_vec.x,
                self.y + aim_vec.y
            ),
        )

        self.__interactor.update(dt)

    def __update_collider(self, dt):
        self.__collider.update(dt)

    def get_bounding_box(self):
        return self.__sprite.get_bounding_box()