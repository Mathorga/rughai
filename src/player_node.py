import math

import pyglet
import pyglet.math as pm
from pyglet.window import key

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

    def get_move_input(self) -> pyglet.math.Vec2:
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
        cam_target: PositionNode = None,
        cam_target_distance: float = 80.0,
        cam_target_offset: tuple = (0.0, 8.0),
        x: int = 0,
        y: int = 0,
        run_threshold: float = 0.75,
        scaling: int = 1
    ) -> None:
        super().__init__(
            x = x,
            y = y
        )

        self.__scaling = scaling

        # IDLE state animations.
        self.__idle_anim = pyglet.resource.animation("sprites/rughai/iryo/iryo_idle.gif")
        self.__walk_anim = pyglet.resource.animation("sprites/rughai/iryo/iryo_walk.gif")
        self.__run_anim = pyglet.resource.animation("sprites/rughai/iryo/iryo_run.gif")
        self.__roll_anim = pyglet.resource.animation("sprites/rughai/iryo/iryo_roll.gif")

        # ATK state animations.
        self.__atk_idle_anim = pyglet.resource.animation("sprites/rughai/iryo/iryo_atk_idle.gif")

        # Center animations.
        utils.center_anim(self.__idle_anim)
        utils.center_anim(self.__walk_anim)
        utils.center_anim(self.__run_anim)
        utils.center_anim(self.__roll_anim)
        utils.center_anim(self.__atk_idle_anim)

        utils.set_anim_duration(self.__roll_anim, 0.08)
        self.__roll_anim.frames[-1].duration = None

        self.__movement = pyglet.math.Vec2()

        # Setup input handling.
        self.__input = PlayerInput(input_controller = input_controller)
        self.__move_input = pyglet.math.Vec2()
        self.__look_input = pyglet.math.Vec2()

        # Movement flags.
        # Slow walking.
        self.__slow = False
        # Currently rolling.
        self.__rolling = False
        # Rolling started.
        self.__rolled = False

        self.__run_threshold = run_threshold

        self.__stats = PlayerStats(
            vitality = 5,
            resistance = 5,
            odds = 5,
            variation = 0.2
        )

        self.__hor_facing: float = 1.0

        self.__sprite = SpriteNode(
            resource = self.__idle_anim,
            on_animation_end = self.on_sprite_animation_end,
            x = x,
            y = y,
            scaling = scaling
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
            on_animation_end = lambda : None,
            x = x,
            y = y,
            scaling = scaling
        )

        self.__cam_target_distance = cam_target_distance
        self.__cam_target_offset = cam_target_offset
        self.__cam_target = cam_target
        self.__cam_target.x = x + cam_target_offset[0]
        self.__cam_target.y = y + cam_target_offset[1]

    def render(self):
        self.__sprite.render()
        self.__aim_sprite.render()

    def update(self, dt) -> None:
        # Fetch input.
        self.input()

        # Update stats based on input.
        self.update_stats(dt)

        # Compute and apply movement to self's x and y coords.
        self.move(dt)

        # Update sprite accordingly.
        self.update_sprite()

        # Update aim sprite.
        self.update_aim()

    def on_sprite_animation_end(self):
        if self.__rolling:
            self.__rolling = False

    def input(self):
        if not self.__rolling:
            self.__move_input = self.__input.get_move_input().limit(1.0)
            self.__look_input = self.__input.get_look_input().limit(1.0)
            self.__slow = self.__input.get_modifier()
            self.__rolling = self.__input.get_sprint()

            if (self.__rolling):
                self.__rolled = True

    def update_stats(self, dt):
        walk_speed = self.__stats._max_speed * 0.5
        roll_speed = self.__stats._max_speed * 2.0
        roll_accel = self.__stats._accel * 0.5

        if self.__rolling:
            if self.__rolled:
                self.__stats._speed = roll_speed
                self.__rolled = False
            else:
                self.__stats._speed -= roll_accel * dt
        else:
            if self.__move_input.mag > 0.0:
                self.__stats._dir = self.__move_input.heading
                self.__stats._speed += self.__stats._accel * dt
            else:
                self.__stats._speed -= self.__stats._accel * dt

        if self.__rolling:
            # Clamp speed between 0 and roll speed.
            self.__stats._speed = pm.clamp(self.__stats._speed, 0.0, roll_speed)
        elif self.__slow:
            # Clamp speed between 0 and walk speed.
            self.__stats._speed = pm.clamp(self.__stats._speed, 0.0, walk_speed)
        else:
            # Clamp speed between 0 and max speed.
            self.__stats._speed = pm.clamp(self.__stats._speed, 0.0, self.__stats._max_speed * self.__move_input.mag)

    def compute_movement(self, dt):
        # Define a vector direction.
        movement_base = pm.Vec2.from_polar(1.0, self.__stats._dir)
        self.__movement = movement_base.from_magnitude(self.__stats._speed * dt)

    def move(self, dt):
        # Compute movement.
        self.compute_movement(dt)

        # Apply movement.
        self.x += self.__movement.x
        self.y += self.__movement.y

    def update_sprite(self):
        # Only update facing if there's any horizontal movement.
        dir_cos = math.cos(self.__stats._dir)
        dir_len = abs(dir_cos)
        if dir_len > 0.1:
            self.__hor_facing = math.copysign(1.0, dir_cos)

        # Update sprite position.
        self.__sprite.set_position(self.x, self.y)

        # Flip sprite if moving to the left.
        self.__sprite.set_scale(x_scale = self.__hor_facing)

        # Update sprite image based on current speed.
        image_to_show = None
        if self.__rolling:
            image_to_show = self.__roll_anim
        else:
            if self.__stats._speed <= 0:
                image_to_show = self.__idle_anim
            elif self.__stats._speed < self.__stats._max_speed * self.__run_threshold:
                image_to_show = self.__walk_anim
            else:
                image_to_show = self.__run_anim
        
        if image_to_show != None and (self.__sprite.get_image() != image_to_show):
            self.__sprite.set_image(image_to_show)

    def update_aim(self):
        aim_vec = pyglet.math.Vec2.from_polar(self.__aim_sprite_distance, self.__stats._dir)
        self.__aim_sprite.set_position(
            self.x + self.__aim_sprite_offset[0] + aim_vec.x,
            self.y + self.__aim_sprite_offset[1] + aim_vec.y
        )

        cam_target_vec = pyglet.math.Vec2.from_polar(self.__cam_target_distance * self.__look_input.mag, self.__look_input.heading)
        self.__cam_target.x = self.x + self.__cam_target_offset[0] + cam_target_vec.x
        self.__cam_target.y = self.y + self.__cam_target_offset[1] + cam_target_vec.y

    def get_bounding_box(self):
        return self.__sprite.get_bounding_box()