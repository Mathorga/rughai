import math
from typing import Optional

import pyglet
import pyglet.math as pm
from pyglet.window import key

from engine.collision.collision_manager import CollisionManager
from engine.collision.collision_node import CollisionNode, CollisionRect, CollisionType
from engine.node import PositionNode
from engine.input_controller import InputController
from engine.sprite_node import SpriteNode
import engine.utils as utils

from player_stats import PlayerStats

class PlayerInput:
    def __init__(
        self,
        input_controller: InputController
    ) -> None:
        self.__controller = input_controller

    def get_modifier(self) -> bool:
        """
        Returns whether or not the modifier key is being pressed, either on controller or keyboard.
        """

        return self.__controller[key.LSHIFT] or self.__controller.buttons.get("leftshoulder", False)

    def get_sprint(self) -> bool:
        """
        Returns whether the sprint button was pressed or not, either on controller or keyboard.
        """

        return self.__controller.key_presses.get(key.SPACE, False) or self.__controller.button_presses.get("b", False)

    def get_main_atk(self) -> bool:
        """
        Returns whether the main attack button was pressed or not, either on controller or keyboard.
        """

        return self.__controller.key_presses.get(key.M, False) or self.__controller.button_presses.get("x", False)

    def get_secondary_atk(self) -> bool:
        """
        Returns whether the secondary attack button was pressed or not, either on controller or keyboard.
        """

        return self.__controller.key_presses.get(key.K, False) or self.__controller.button_presses.get("y", False)

    def get_fire_aim(self) -> bool:
        """
        Returns whether the range attack aim button was pressed or not.
        """

        return self.__controller.triggers.get("lefttrigger", 0.0) > 0.0

    def get_fire_load(self) -> bool:
        """
        Returns whether the range attack load button was pressed or not.
        """

        return self.__controller.triggers.get("righttrigger", 0.0) > 0.0

    def get_move_input(self) -> pyglet.math.Vec2:
        """
        Returns the movement vector from keyboard and controller.
        """

        stick = self.__controller.sticks.get("leftstick", (0.0, 0.0))
        return pyglet.math.Vec2(
            (self.__controller[key.D] - self.__controller[key.A]) + stick[0],
            (self.__controller[key.W] - self.__controller[key.S]) + stick[1]
        )

    def get_look_input(self) -> pyglet.math.Vec2:
        stick = self.__controller.sticks.get("rightstick", (0.0, 0.0))
        return pyglet.math.Vec2(
            (self.__controller[key.RIGHT] - self.__controller[key.LEFT]) + stick[0],
            (self.__controller[key.UP] - self.__controller[key.DOWN]) + stick[1]
        )

class PlayerNode(PositionNode):
    def __init__(
        self,
        input_controller: InputController,
        collision_manager: CollisionManager,
        cam_target: PositionNode,
        cam_target_distance: float = 50.0,
        cam_target_offset: tuple = (0.0, 8.0),
        x: int = 0,
        y: int = 0,
        run_threshold: float = 0.75,
        scaling: int = 1,
        collision_tag: str = "",
        order: int = 0,
        batch: Optional[pyglet.graphics.Batch] = None
    ) -> None:
        PositionNode.__init__(
            self,
            x = x,
            y = y
        )

        self.__scaling = scaling

        # IDLE state animations.
        self.__idle_anim = pyglet.resource.animation("sprites/rughai/iryo/iryo_idle.gif")
        self.__walk_anim = pyglet.resource.animation("sprites/rughai/iryo/iryo_walk.gif")
        self.__run_anim = pyglet.resource.animation("sprites/rughai/iryo/iryo_run.gif")
        self.__sprint_anim = pyglet.resource.animation("sprites/rughai/iryo/iryo_roll.gif")

        # ATK state animations.
        self.__atk_idle_anim = pyglet.resource.animation("sprites/rughai/iryo/iryo_atk_idle.gif")
        self.__atk_0_anim = pyglet.resource.animation("sprites/rughai/iryo/iryo_atk_0.gif")

        # Center animations.
        utils.center_anim(self.__idle_anim)
        utils.center_anim(self.__walk_anim)
        utils.center_anim(self.__run_anim)
        utils.center_anim(self.__sprint_anim)
        utils.center_anim(self.__atk_idle_anim)
        utils.center_anim(self.__atk_0_anim)
        self.__atk_0_anim.frames[-1].duration = None

        utils.set_anim_duration(self.__sprint_anim, 0.08)
        self.__sprint_anim.frames[-1].duration = None

        self.__movement = pyglet.math.Vec2()

        # Setup input handling.
        self.__controls_enabled = True
        self.__input = PlayerInput(input_controller = input_controller)
        self.__move_input = pyglet.math.Vec2()
        self.__look_input = pyglet.math.Vec2()

        # Movement flags.
        self.__slow = False

        # Sprinting flags.
        self.__sprint_ing = False
        self.__sprint_ed = False

        # Atk flags
        self.__main_atk_ing = False
        self.__main_atk_ed = False

        self.__run_threshold = run_threshold

        self.__stats = PlayerStats(
            vitality = 5,
            resistance = 5,
            odds = 5,
            variation = 0.2
        )

        self.__hor_facing: int = 1

        self.__sprite = SpriteNode(
            resource = self.__idle_anim,
            on_animation_end = self.on_sprite_animation_end,
            x = x,
            y = y,
            scaling = scaling,
            batch = batch
        )

        # Aim sprite image.
        target_image = pyglet.resource.image("sprites/target.png")
        target_image.anchor_x = target_image.width / 2
        target_image.anchor_y = target_image.height / 2

        # Aim sprite offset, defines the offset from self.x and self.y, respectively.
        self.__aim_sprite_offset = (0.0, 8.0)

        # Aim sprite distance, defines the distance at which the sprite floats.
        self.__aim_sprite_distance = 10.0
        self.__aim_sprite = SpriteNode(
            resource = target_image,
            x = x,
            y = y,
            scaling = scaling,
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
            scaling = scaling,
            batch = batch
        )

        # Collider.
        self.__collider = CollisionNode(
            x = x,
            y = y,
            scaling = scaling,
            type = CollisionType.DYNAMIC,
            tag = collision_tag,
            shapes = [
                CollisionRect(
                    x = x,
                    y = y,
                    width = 8,
                    height = 6,
                    anchor_x = 4,
                    anchor_y = 3,
                    scaling = scaling,
                    batch = batch
                )
            ],
            batch = batch
        )
        collision_manager.add_collider(self.__collider)

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

        # Update sprites accordingly.
        self.__update_sprites(dt)

    def on_sprite_animation_end(self):
        if self.__sprint_ing:
            self.__sprint_ing = False

        if self.__main_atk_ing:
            self.__main_atk_ing = False

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

            # All other input should be fetched if not rolling.
            if self.__sprint_ing or self.__main_atk_ing:
                return

            self.__move_input = self.__input.get_move_input().limit(1.0)
            self.__slow = self.__input.get_modifier()

            self.__sprint_ing = self.__input.get_sprint()
            if self.__sprint_ing:
                self.__sprint_ed = True

            self.__main_atk_ing = self.__input.get_main_atk()
            if self.__main_atk_ing:
                self.__main_atk_ed = True

    def __update_dir(self):
        if self.__move_input.mag > 0.0:
            self.__stats._dir = self.__move_input.heading

    def __update_stats(self, dt):
        walk_speed = self.__stats._max_speed * 0.5
        roll_speed = self.__stats._max_speed * 2.0
        roll_accel = self.__stats._accel * 0.5

        if self.__sprint_ing:
            # Sprinting.
            if self.__sprint_ed:
                # Update direction in order to correctly orient sprints.
                self.__update_dir()

                self.__stats._speed = roll_speed
                self.__sprint_ed = False
            else:
                self.__stats._speed -= roll_accel * dt
        elif self.__main_atk_ing:
            # Main attacking.
            if self.__main_atk_ed:
                self.__update_dir()

                self.__stats._speed = 0.0
                self.__main_atk_ed = False
        else:
            if self.__move_input.mag > 0.0:
                self.__stats._dir = self.__move_input.heading
                self.__stats._speed += self.__stats._accel * dt
            else:
                self.__stats._speed -= self.__stats._accel * dt

        if self.__sprint_ing:
            # Clamp speed between 0 and roll speed.
            self.__stats._speed = pm.clamp(self.__stats._speed, 0.0, roll_speed)
        elif self.__slow:
            # Clamp speed between 0 and walk speed.
            self.__stats._speed = pm.clamp(self.__stats._speed, 0.0, walk_speed)
        else:
            # Clamp speed between 0 and max speed.
            self.__stats._speed = pm.clamp(self.__stats._speed, 0.0, self.__stats._max_speed)

    def __compute_movement(self, dt):
        # Define a vector direction.
        movement_base = pm.Vec2.from_polar(1.0, self.__stats._dir)

        # Scale movement to current speed.
        self.__movement = movement_base.from_magnitude(self.__stats._speed * dt)

    def __move(self, dt):
        # Compute movement.
        self.__compute_movement(dt)

        # Apply movement.
        self.x += self.__movement.x
        self.y += self.__movement.y

    def __update_sprites(self, dt):
        # Only update facing if there's any horizontal movement.
        dir_cos = math.cos(self.__stats._dir)
        dir_len = abs(dir_cos)
        if dir_len > 0.1:
            self.__hor_facing = int(math.copysign(1.0, dir_cos))

        # Update sprite position.
        self.__sprite.set_position(self.x, self.y)

        # Flip sprite if moving to the left.
        self.__sprite.set_scale(x_scale = self.__hor_facing)

        # Update sprite image based on current speed.
        image_to_show = None
        if self.__sprint_ing:
            image_to_show = self.__sprint_anim
        elif self.__main_atk_ing:
            image_to_show = self.__atk_0_anim
        else:
            if self.__stats._speed <= 0:
                image_to_show = self.__idle_anim
            elif self.__stats._speed < self.__stats._max_speed * self.__run_threshold:
                image_to_show = self.__walk_anim
            else:
                image_to_show = self.__run_anim
        
        # if image_to_show != None and self.__sprite.get_image() != image_to_show:
        self.__sprite.set_image(image_to_show)
        self.__sprite.update(dt = dt)

        # Update aim sprite.
        self.__update_aim(dt)

        # Update camera target.
        self.__update_cam_target(dt)

        # Update shadow sprite.
        self.__update_shadow(dt)

        # Update collider.
        self.__update_collider(dt)

    def __update_aim(self, dt):
        aim_vec = pyglet.math.Vec2.from_polar(self.__aim_sprite_distance, self.__stats._dir)
        self.__aim_sprite.set_position(
            self.x + self.__aim_sprite_offset[0] + aim_vec.x,
            self.y + self.__aim_sprite_offset[1] + aim_vec.y
        )
        self.__aim_sprite.update(dt)


    def __update_cam_target(self, dt):
        cam_target_vec = pyglet.math.Vec2.from_polar(self.__cam_target_distance * self.__look_input.mag, self.__look_input.heading)
        self.__cam_target.x = self.x + self.__cam_target_offset[0] + cam_target_vec.x
        self.__cam_target.y = self.y + self.__cam_target_offset[1] + cam_target_vec.y
        self.__cam_target.update(dt)

    def __update_shadow(self, dt):
        self.__shadow_sprite.set_position(self.x, self.y)
        self.__shadow_sprite.update(dt)

    def __update_collider(self, dt):
        self.__collider.set_position(self.x, self.y)
        self.__collider.update(dt)

    def get_bounding_box(self):
        return self.__sprite.get_bounding_box()