"""
Module containing the main player class.
"""

import math
from typing import Optional

import pyglet
import pyglet.math as pm
from aim_node import AimNode

from constants import collision_tags
from engine.animation import Animation

from engine.collision.collision_node import CollisionNode, CollisionType
from engine.collision.collision_shape import CollisionRect
from engine.node import PositionNode
from engine.sprite_node import SpriteNode
from engine.settings import SETTINGS, Builtins

import engine.controllers as controllers
from player_stats import PlayerStats

class PlayerNode(PositionNode):
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

        # IDLE state animations.
        self.__idle_anim = Animation(source = "sprites/iryo/iryo_idle.json")
        self.__walk_anim = Animation(source = "sprites/iryo/iryo_walk.json")
        self.__run_anim = Animation(source = "sprites/iryo/iryo_run.json")
        self.__sprint_anim = Animation(source = "sprites/iryo/iryo_roll.json")

        # ATK state animations.
        self.__atk_idle_anim = Animation(source = "sprites/iryo/iryo_atk_idle.json")
        self.__atk_load_anim = Animation(source = "sprites/iryo/iryo_atk_load.json")
        self.__atk_hold_0_anim = Animation(source = "sprites/iryo/iryo_atk_hold_0.json")
        self.__atk_hold_0_walk_anim = Animation(source = "sprites/iryo/iryo_atk_hold_0_walk.json")
        self.__atk_hold_1_anim = Animation(source = "sprites/iryo/iryo_atk_hold_1.json")
        self.__atk_hold_1_walk_anim = Animation(source = "sprites/iryo/iryo_atk_hold_1_walk.json")
        self.__atk_hold_2_anim = Animation(source = "sprites/iryo/iryo_atk_hold_2.json")
        self.__atk_shoot_0_anim = Animation(source = "sprites/iryo/iryo_atk_shoot_0.json")
        self.__atk_shoot_1_anim = Animation(source = "sprites/iryo/iryo_atk_shoot_1.json")
        self.__atk_shoot_2_anim = Animation(source = "sprites/iryo/iryo_atk_shoot_2.json")

        self.__interactor_distance = 5.0

        # Setup input handling.
        self.__controls_enabled = False
        self.__move_input = pyglet.math.Vec2()
        self.__look_input = pyglet.math.Vec2()

        # Movement flags.
        self.__slow = False

        # Sprinting flags.
        self.__sprint_ing = False
        self.__sprint_ed = False

        # Atk flags
        self.__loading = False
        self.__aiming = False
        self.__loading = False
        self.__shoot_ing = False
        self.__shoot_ed = False
        self.__drawing = False

        self.__run_threshold = run_threshold

        self.__stats = PlayerStats(
            vitality = 5,
            resistance = 5,
            odds = 5,
            variation = 0.2
        )

        self.__hor_facing: int = 1

        self.__sprite = SpriteNode(
            resource = self.__idle_anim.animation,
            on_animation_end = self.on_sprite_animation_end,
            x = x,
            y = y,
            batch = batch
        )

        # Aim target.
        self.__aim = AimNode(
            x = self.x,
            y = self.y,
            offset_y = 8.0,
            batch = batch
        )

        # Shadow sprite image.
        shadow_image = pyglet.resource.image("sprites/shadow.png")
        shadow_image.anchor_x = shadow_image.width / 2
        shadow_image.anchor_y = shadow_image.height / 2

        self.__shadow_sprite = SpriteNode(
            resource = shadow_image,
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

        # Interaction finder.
        # This collider is responsible for searching for interactables.
        self.__interactor = CollisionNode(
            x = x,
            y = y,
            sensor = True,
            collision_type = CollisionType.DYNAMIC,
            tags = [collision_tags.PLAYER_INTERACTION],
            shapes = [
                CollisionRect(
                    x = x,
                    y = y,
                    anchor_x = 4,
                    anchor_y = 4,
                    width = 8,
                    height = 8,
                    batch = batch
                )
            ]
        )
        controllers.COLLISION_CONTROLLER.add_collider(self.__interactor)

        self.__cam_target_distance = cam_target_distance
        self.__cam_target_offset = cam_target_offset
        self.__cam_target = cam_target
        self.__cam_target.x = x + cam_target_offset[0]
        self.__cam_target.y = y + cam_target_offset[1]

    def delete(self) -> None:
        self.__sprite.delete()
        self.__aim_sprite.delete()
        self.__shadow_sprite.delete()
        self.__collider.delete()
        self.__interactor.delete()

    def draw(self):
        # Draw collider out of batch.
        self.__collider.draw()

        self.__shadow_sprite.draw()
        self.__sprite.draw()
        self.__aim_sprite.draw()

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

    def on_sprite_animation_end(self):
        if self.__sprint_ing:
            self.__sprint_ing = False

        if self.__loading:
            self.__loading = False
            self.__aiming = True

    def disable_controls(self) -> None:
        """
        Disables user controls over the player and stops all existing inputs.
        """

        self.__look_input = pm.Vec2()
        self.__move_input = pm.Vec2()
        self.__controls_enabled = False

    def enable_controls(self) -> None:
        """
        Enables user controls over the player.
        """

        self.__controls_enabled = True

    def get_aim_dir(self) -> float:
        """
        Computes the right aim direction according to the current aim state: look direction when aiming, move direction when not aiming.
        """

        return self.__stats.look_dir if self.__aiming or self.__loading else self.__stats.move_dir

    def __fetch_input(self):
        if self.__controls_enabled:
            # Check whether there's any aim input or not.
            aiming = controllers.INPUT_CONTROLLER.get_view_input()

            # Get actual aim input.
            self.__look_input = controllers.INPUT_CONTROLLER.get_view_movement().limit(1.0)

            if aiming:
                if not self.__loading and not self.__aiming:
                    self.__loading = True
            else:
                self.__loading = False
                self.__aiming = False
                self.__drawing = False

            if self.__aiming:
                self.__drawing = controllers.INPUT_CONTROLLER.get_draw()

            if not self.__sprint_ing and not self.__loading:
                self.__move_input = controllers.INPUT_CONTROLLER.get_movement().limit(1.0)

            if not self.__loading and not self.__aiming and not self.__sprint_ing:
                self.__sprint_ing = controllers.INPUT_CONTROLLER.get_sprint()
                if self.__sprint_ing:
                    self.__sprint_ed = True

            self.__slow = controllers.INPUT_CONTROLLER.get_modifier() or self.__aiming

            if not self.__loading and not self.__aiming:
                # Interaction.
                interact = controllers.INPUT_CONTROLLER.get_interaction()
                if interact:
                    controllers.INTERACTION_CONTROLLER.interact()

    def __update_dir(self):
        if self.__move_input.mag > 0.0:
            self.__stats.move_dir = self.__move_input.heading

        if self.__look_input.mag > 0.0:
            self.__stats.look_dir = self.__look_input.heading
        else:
            if not self.__loading and not self.__aiming:
                self.__stats.look_dir = self.__stats.move_dir

    def __update_stats(self, dt):
        aim_speed = self.__stats.max_speed * 0.2
        walk_speed = self.__stats.max_speed * 0.5
        roll_speed = self.__stats.max_speed * 2.0
        roll_accel = self.__stats.accel * 0.5

        if self.__loading:
            self.__update_dir()
            self.__stats.speed = 0.0
        elif self.__drawing:
            self.__update_dir()
            self.__stats.speed = aim_speed
        elif self.__sprint_ing:
            # Sprinting.
            if self.__sprint_ed:
                # Update direction in order to correctly orient sprints.
                self.__update_dir()

                self.__stats.speed = roll_speed
                self.__sprint_ed = False
            else:
                self.__stats.speed -= roll_accel * dt
        else:
            self.__update_dir()
            if self.__move_input.mag > 0.0:
                self.__stats.speed += self.__stats.accel * dt
            else:
                self.__stats.speed -= self.__stats.accel * dt

        if self.__sprint_ing:
            # Clamp speed between 0 and roll speed.
            self.__stats.speed = pm.clamp(self.__stats.speed, 0.0, roll_speed)
        elif self.__slow:
            # Clamp speed between 0 and walk speed.
            self.__stats.speed = pm.clamp(self.__stats.speed, 0.0, walk_speed)
        else:
            # Clamp speed between 0 and max speed.
            self.__stats.speed = pm.clamp(self.__stats.speed, 0.0, self.__stats.max_speed)

    def __compute_velocity(self, dt) -> pm.Vec2:
        # Define a vector from speed and direction.
        return pm.Vec2.from_polar(self.__stats.speed * dt, self.__stats.move_dir)

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
        dir_cos = math.cos(self.get_aim_dir())
        dir_len = abs(dir_cos)
        if dir_len > 0.1:
            self.__hor_facing = int(math.copysign(1.0, dir_cos))

        # Update sprite position.
        self.__sprite.set_position((self.x, self.y))

        # Flip sprite if moving to the left.
        self.__sprite.set_scale(x_scale = self.__hor_facing)

        # Update sprite image based on current state.
        image_to_show = None
        if self.__drawing:
            if self.__stats.speed <= 0:
                image_to_show = self.__atk_hold_1_anim.animation
            else:
                image_to_show = self.__atk_hold_1_walk_anim.animation
        elif self.__loading:
            image_to_show = self.__atk_load_anim.animation
        elif self.__aiming:
            if self.__stats.speed <= 0:
                image_to_show = self.__atk_hold_0_anim.animation
            else:
                image_to_show = self.__atk_hold_0_walk_anim.animation
        elif self.__sprint_ing:
            image_to_show = self.__sprint_anim.animation
        else:
            if self.__stats.speed <= 0:
                image_to_show = self.__idle_anim.animation
            elif self.__stats.speed < self.__stats.max_speed * self.__run_threshold:
                image_to_show = self.__walk_anim.animation
            else:
                image_to_show = self.__run_anim.animation
        
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
        """
        Updates the aim sign.
        """

        self.__aim.set_direction(direction = self.get_aim_dir())
        self.__aim.set_position(position = self.get_position())
        self.__aim.update(dt = dt)

    def __update_shadow(self, dt):
        self.__shadow_sprite.set_position(
            position = (self.x, self.y),
            # z = 0
            z = -(self.y + (SETTINGS[Builtins.LAYERS_Z_SPACING] * 0.5))
        )
        self.__shadow_sprite.update(dt)

    def __update_cam_target(self, dt):
        # Automatically go to cam target distance if loading or aiming.
        cam_target_distance = self.__cam_target_distance if self.__loading or self.__aiming else self.__cam_target_distance * self.__look_input.mag

        cam_target_vec = pyglet.math.Vec2.from_polar(cam_target_distance, self.__stats.look_dir)
        self.__cam_target.x = self.x + self.__cam_target_offset[0] + cam_target_vec.x
        self.__cam_target.y = self.y + self.__cam_target_offset[1] + cam_target_vec.y
        self.__cam_target.update(dt)

    def __update_interactor(self, dt):
        aim_vec = pyglet.math.Vec2.from_polar(self.__interactor_distance, self.get_aim_dir())
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